import asyncio
import io
import uuid
from asyncio import AbstractEventLoop
from concurrent.futures import ThreadPoolExecutor
from typing import Final, cast

from PIL import Image
from PIL.ImageFile import ImageFile
from nsfw_image_detector import NSFWDetector, NSFWLevel

from nsfw_detector.application.common.ports.images.query_gateway import ImageQueryGateway
from nsfw_detector.application.queries.images.view_models import NSFWImageInformation


class NSFWDetectorImageQueryGateway(ImageQueryGateway):
    def __init__(self, detector: NSFWDetector) -> None:
        self._detector: Final[NSFWDetector] = detector
        self._thread_pool_executor: Final[ThreadPoolExecutor] = ThreadPoolExecutor(max_workers=4)

    async def check_image_is_nsfw_by_file(self, data: bytes) -> NSFWImageInformation:
        loop: AbstractEventLoop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            self._thread_pool_executor,
            self.__process_image_in_executor,
            data
        )

    def __process_image_in_executor(self, data: bytes) -> NSFWImageInformation:
        pillow_image: ImageFile = Image.open(io.BytesIO(data))
        dictionary_with_labels: dict[NSFWLevel, float] = cast(
            dict[NSFWLevel, float],
            self._detector.predict_proba(pillow_image)
        )

        return NSFWImageInformation(
            request_id=str(uuid.uuid4()),
            status="success",
            output=str(dictionary_with_labels[NSFWLevel.NEUTRAL])
        )
