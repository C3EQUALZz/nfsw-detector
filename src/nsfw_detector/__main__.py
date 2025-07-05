import asyncio
import logging
from typing import Final

import uvicorn
from fastapi import FastAPI

from nsfw_detector.setup.bootstrap import setup_configs, setup_logging
from nsfw_detector.setup.configs import Configs
from nsfw_detector.web import create_app_production

logger: Final[logging.Logger] = logging.getLogger(__name__)


async def create_uvicorn_server(app: FastAPI) -> None:
    configs: Configs = setup_configs()
    setup_logging(logger_config=configs.logging)

    config: uvicorn.Config = uvicorn.Config(
        app=app,
        host=configs.asgi.host,
        port=configs.asgi.port,
        log_level=logging.INFO,
    )

    server = uvicorn.Server(config)
    logger.info("Running API")
    await server.serve()


def main() -> None:
    asyncio.run(create_uvicorn_server(create_app_production()))


if __name__ == "__main__":
    main()
