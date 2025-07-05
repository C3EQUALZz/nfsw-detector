import logging
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Final

import pydantic
from fastapi import FastAPI, status
from fastapi.encoders import jsonable_encoder
from fastapi.requests import Request
from fastapi.responses import ORJSONResponse

from nsfw_detector.application.common.errors.base import ApplicationError
from nsfw_detector.application.common.errors.images import NotAllowedExtensionOfImage, FailedToProcessImage
from nsfw_detector.infrastructure.errors.base import (
    InfrastructureError,
)

logger: Final[logging.Logger] = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class ExceptionSchema:
    description: str


@dataclass(frozen=True, slots=True)
class ExceptionSchemaRich:
    description: str
    details: list[dict[str, Any]] | None = None


class ExceptionHandler:
    _ERROR_MAPPING: Final[MappingProxyType[type[Exception], int]] = MappingProxyType({
        # 400
        FailedToProcessImage: status.HTTP_400_BAD_REQUEST,
        # 422
        pydantic.ValidationError: status.HTTP_422_UNPROCESSABLE_ENTITY,
        NotAllowedExtensionOfImage: status.HTTP_422_UNPROCESSABLE_ENTITY,

        # 500
        ApplicationError: status.HTTP_500_INTERNAL_SERVER_ERROR,
        InfrastructureError: status.HTTP_500_INTERNAL_SERVER_ERROR,
        Exception: status.HTTP_500_INTERNAL_SERVER_ERROR,
    })

    def __init__(self, app: FastAPI):
        self._app = app

    async def _handle(self, _: Request, exc: Exception) -> ORJSONResponse:
        status_code: int = self._ERROR_MAPPING.get(
            type(exc),
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

        response: ExceptionSchema | ExceptionSchemaRich
        if isinstance(exc, pydantic.ValidationError):
            response = ExceptionSchemaRich(str(exc), jsonable_encoder(exc.errors()))

        elif status_code == status.HTTP_503_SERVICE_UNAVAILABLE:
            message_if_unavailable: str = "Service temporarily unavailable. Please try again later."
            response = ExceptionSchema(message_if_unavailable)

        else:
            message: str = str(exc) if status_code < 500 else "Internal server error."
            response = ExceptionSchema(message)

        if status_code >= 500:
            logger.error(
                "Exception '%s' occurred: '%s'.",
                type(exc).__name__,
                exc,
                exc_info=exc,
            )

        else:
            logger.warning("Exception '%s' occurred: '%s'.", type(exc).__name__, exc)

        return ORJSONResponse(
            status_code=status_code,
            content=response,
        )

    def setup_handlers(self) -> None:
        for exc_class in self._ERROR_MAPPING:
            self._app.add_exception_handler(exc_class, self._handle)
        self._app.add_exception_handler(Exception, self._handle)
