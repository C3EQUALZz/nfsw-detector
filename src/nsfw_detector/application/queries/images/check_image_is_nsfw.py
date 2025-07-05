from dataclasses import dataclass
from typing import final, Final, Iterable

from nsfw_detector.application.common.errors.images import NotAllowedExtensionOfImage, FailedToProcessImage
from nsfw_detector.application.common.ports.images.query_gateway import ImageQueryGateway
from nsfw_detector.application.queries.images.view_models import NSFWImageInformation

ALLOWED_EXTENSIONS: Final[Iterable[str]] = ("jpg", "png")
MINIMAL_NSFW_SCORE: Final[float] = 0.7


@dataclass(frozen=True, slots=True)
class CheckImageIsNSFWQuery:
    content_of_image: bytes
    filename_with_extension: str


@final
class CheckImageIsNSFWQueryHandler:
    def __init__(
            self,
            image_query_gateway: ImageQueryGateway
    ) -> None:
        """
        Query for getting information if image contains NSFW content,
        :param image_query_gateway: image gateway
        """
        self._image_query_gateway: Final[ImageQueryGateway] = image_query_gateway

    async def __call__(self, data: CheckImageIsNSFWQuery) -> bool:
        if not any(data.filename_with_extension.endswith(extension) for extension in (".png", ".jpg")):
            raise NotAllowedExtensionOfImage(
                f"{data.filename_with_extension} is not an allowed extensions."
                f" Please provide image with extensions: {', '.join(ALLOWED_EXTENSIONS)}"
            )

        information_about_image: NSFWImageInformation = await self._image_query_gateway.check_image_is_nsfw_by_file(
            data=data.content_of_image
        )

        if information_about_image.status != "success":
            raise FailedToProcessImage(f"{data.filename_with_extension} can't be processed. Please try again later.")

        return float(information_about_image.output) > MINIMAL_NSFW_SCORE

