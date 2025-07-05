from typing import Final

from fastapi import APIRouter, Request

router: Final[APIRouter] = APIRouter(tags=["Main"])


@router.get("/")
async def index(_: Request) -> dict[str, str]:
    """Root endpoint of the API.

    Provides a welcome message and confirms that the API is operational.
    Typically used as the initial entry point to verify API availability.

    Args:
        _: FastAPI Request object (unused in this endpoint)

    Returns:
        dict[str, str]: Welcome message containing:
            - "message": Greeting text confirming API availability

    Notes:
        - This endpoint always returns HTTP 200 when service is running
        - Serves as the API's root path (/)
        - Part of the 'Main' tag group in OpenAPI documentation
    """
    return {"message": "Hello there! Welcome to API!"}