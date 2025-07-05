import logging
from functools import lru_cache

from fastapi import APIRouter, FastAPI
from starlette.middleware.cors import CORSMiddleware

from nsfw_detector.presentation.http.common.routes import healthcheck, index
from nsfw_detector.presentation.http.common.exception_handlers import ExceptionHandler
from nsfw_detector.presentation.http.v1.routes import images
from nsfw_detector.setup.configs import LoggingConfig
from nsfw_detector.setup.configs import (
    ASGIConfig,
    Configs,
)


@lru_cache(maxsize=1)
def setup_configs() -> Configs:
    return Configs()


def setup_middlewares(app: FastAPI, /, api_config: ASGIConfig) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            f"http://localhost:{api_config.port}",
            f"https://{api_config.host}:{api_config.port}",
        ],
        allow_credentials=api_config.allow_credentials,
        allow_methods=api_config.allow_methods,
        allow_headers=api_config.allow_headers,
    )


def setup_routes(app: FastAPI, /) -> None:
    """
    Registers all routers for FastAPI application

    Args:
        app: FastAPI application

    Returns:
        None
    """
    app.include_router(index.router)
    app.include_router(healthcheck.router)

    router_v1: APIRouter = APIRouter(prefix="/v1")
    router_v1.include_router(images.router)

    app.include_router(router_v1)


def setup_exc_handlers(app: FastAPI) -> None:
    """
    Registers exception handlers for the FastAPI application.

    Args:
        app: FastAPI application instance to configure
    """
    exception_handler: ExceptionHandler = ExceptionHandler(app)
    exception_handler.setup_handlers()


def setup_logging(logger_config: LoggingConfig) -> None:
    """
    Setup logging configuration.
    In production I would recommend to use structlog.
    """
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%m/%d/%Y %I:%M:%S %p",
        level=logger_config.default_level,
    )
