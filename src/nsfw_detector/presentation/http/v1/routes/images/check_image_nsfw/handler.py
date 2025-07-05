import logging
from typing import Final, Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, UploadFile, File
from starlette import status

from nsfw_detector.application.queries.images.check_image_is_nsfw import (
    CheckImageIsNSFWQueryHandler,
    CheckImageIsNSFWQuery
)
from nsfw_detector.presentation.http.v1.routes.images.check_image_nsfw.schemas import (
    CheckImageIsNSFWResponseSchema
)

logger: Final[logging.Logger] = logging.getLogger(__name__)
router: Final[APIRouter] = APIRouter(route_class=DishkaRoute)


@router.post(
    "/moderate",
    summary="Moderate image for nsfw",
    status_code=status.HTTP_200_OK,
    description="Api handler for moderating image if it has nsfw content. Returns True if nsfw score > 0.7",
    response_model_exclude_none=True,
)
async def handle_check_image_nsfw(
        image: Annotated[UploadFile, File(
            description="File with jpg and png extension",
            examples=["super.jpg", "puper.png"]
        )],
        interactor: FromDishka[CheckImageIsNSFWQueryHandler]
) -> CheckImageIsNSFWResponseSchema:
    query: CheckImageIsNSFWQuery = CheckImageIsNSFWQuery(
        content_of_image=image.file.read(),
        filename_with_extension=image.filename
    )

    response_from_interactor: bool | None = await interactor(query)

    if response_from_interactor:
        return CheckImageIsNSFWResponseSchema(
            status="OK"
        )

    return CheckImageIsNSFWResponseSchema(
        status="REJECTED",
        reason="NSFW content"
    )
