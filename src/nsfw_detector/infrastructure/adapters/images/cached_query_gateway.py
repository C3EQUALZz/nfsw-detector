import hashlib
import uuid

from nsfw_detector.application.common.ports.images.query_gateway import ImageQueryGateway
from nsfw_detector.application.queries.images.view_models import NSFWImageInformation
from nsfw_detector.infrastructure.cache.base import CacheStore, KeyWithPrefix, Prefix, Key
from typing import Final


class ImageCachedQueryGateway(ImageQueryGateway):
    def __init__(
            self,
            gateway: ImageQueryGateway,
            cache_store: CacheStore,
    ) -> None:
        self._gateway: Final[ImageQueryGateway] = gateway
        self._cache_store: Final[CacheStore] = cache_store

    async def check_image_is_nsfw_by_file(self, data: bytes) -> NSFWImageInformation:
        key_with_prefix = KeyWithPrefix(
            prefix=Prefix("nsfw_image"),
            key=Key(self.__generate_image_hash(data))
        )

        exists: bool = await self._cache_store.exists(key_with_prefix)

        if exists:
            return NSFWImageInformation(
                request_id=str(uuid.uuid4()),
                status="success",
                output=await self._cache_store.get(key_with_prefix)
            )

        nsfw_image_information: NSFWImageInformation = await self._gateway.check_image_is_nsfw_by_file(
            data=data,
        )

        await self._cache_store.set(
            key=key_with_prefix,
            value=nsfw_image_information.output,
            ttl=50
        )

        return nsfw_image_information

    @staticmethod
    def __generate_image_hash(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()
