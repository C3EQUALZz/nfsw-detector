import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any, Final, cast

from dishka import AsyncContainer, make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

import nsfw_detector
from nsfw_detector.setup.bootstrap import (
    setup_configs,
    setup_exc_handlers,
    setup_middlewares,
    setup_routes
)
from nsfw_detector.setup.configs import (
    ASGIConfig,
    Configs, GenAPIConfig, RedisConfig,
)
from nsfw_detector.setup.ioc import setup_providers

logger: Final[logging.Logger] = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI, /) -> AsyncIterator[None]:
    """Async context manager for FastAPI application lifecycle management.

    Handles the startup and shutdown events of the FastAPI application.
    Specifically ensures proper cleanup
        of Dishka container resources on shutdown.

    Args:
        app: FastAPI application instance. Positional-only parameter.

    Yields:
        None: Indicates successful entry into the context.

    Note:
        The actual resource cleanup (Dishka container closure)
            happens after yield, during the application shutdown phase.
    """
    yield None
    await cast("AsyncContainer", app.state.dishka_container).close()


def create_app_tests() -> FastAPI:
    app: FastAPI = FastAPI(
        lifespan=lifespan,
        default_response_class=ORJSONResponse,
        version=nsfw_detector.__version__,
        root_path="/api",
        debug=True,
    )
    configs: Configs = setup_configs()
    context: dict[Any, Any] = {
        ASGIConfig: configs.asgi,
        GenAPIConfig: configs.genai,
        RedisConfig: configs.redis,
    }
    container: AsyncContainer = make_async_container(*setup_providers(), context=context)
    setup_routes(app)
    setup_exc_handlers(app)
    setup_middlewares(app, api_config=configs.asgi)
    setup_dishka(container, app)
    logger.info("App created")
    return app


def create_app_production() -> FastAPI:  # pragma: no cover
    """Creates and configures a FastAPI application
        instance with all dependencies.

    Performs comprehensive application setup including:
    - Configuration initialization
    - Dependency injection container setup
    - Route registration
    - Exception handlers
    - Observability tools
    - Middleware stack
    - Dishka integration

    Returns:
        FastAPI: Fully configured application instance ready for use.

    Side Effects:
        - Configures global application state
        - Registers all route handlers
    """
    configs: Configs = setup_configs()

    app: FastAPI = FastAPI(
        lifespan=lifespan,
        default_response_class=ORJSONResponse,
        version=nsfw_detector.__version__,
        root_path="/api",
        debug=configs.asgi.fastapi_debug,
    )
    context: dict[Any, Any] = {
        ASGIConfig: configs.asgi,
        GenAPIConfig: configs.genai,
        RedisConfig: configs.redis,
    }
    container: AsyncContainer = make_async_container(*setup_providers(), context=context)
    setup_routes(app)
    setup_exc_handlers(app)
    setup_middlewares(app, api_config=configs.asgi)
    setup_dishka(container, app)
    logger.info("App created")
    return app
