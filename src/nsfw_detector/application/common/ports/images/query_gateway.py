from abc import abstractmethod
from typing import Protocol

from nsfw_detector.application.queries.images.view_models import NSFWImageInformation


class ImageQueryGateway(Protocol):
    @abstractmethod
    async def check_image_is_nsfw_by_file(self, data: bytes) -> NSFWImageInformation:
        ...
