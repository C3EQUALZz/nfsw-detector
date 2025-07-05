from typing import Final

from fastapi import APIRouter

from nsfw_detector.presentation.http.v1.routes.images.check_image_nsfw.handler import (
    router as check_image_nsfw_router,
)

router: Final[APIRouter] = APIRouter(
    prefix="/images",
    tags=["Images"],
)

users_sub_routers: tuple[APIRouter, ...] = (
    check_image_nsfw_router,
)

for sub_router in users_sub_routers:
    router.include_router(sub_router)