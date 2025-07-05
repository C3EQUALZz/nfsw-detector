import os
from pydantic import BaseModel, Field
from typing import Literal


class LoggingConfig(BaseModel):
    default_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Default logging level",
    )


class RedisConfig(BaseModel):
    host: str = Field(
        alias="REDIS_HOST",
        default="localhost",
        description="Redis host",
        validate_default=True
    )
    port: int = Field(
        alias="REDIS_PORT",
        default=6379,
        description="Redis port",
        validate_default=True
    )
    user: str = Field(
        alias="REDIS_USER",
        default="root",
        description="Redis user",
        validate_default=True
    )
    password: str = Field(
        alias="REDIS_PASSWORD",
        default="<PASSWORD>",
        description="Redis password",
        validate_default=True
    )
    db: int = Field(
        alias="REDIS_DB",
        default=0,
        description="Redis db",
        validate_default=True
    )

    @property
    def url(self) -> str:
        return f"redis://{self.host}:{self.port}/0"


class GenAPIConfig(BaseModel):
    api_key: str = Field(
        ...,
        alias="API_KEY_FOR_NSFW_CONTENT",
        description="API key for NSFW content filtering for GenAI",
    )


class ASGIConfig(BaseModel):
    """Configuration container for ASGI server settings.

    Attributes:
        host: Interface to bind the server to (e.g., '0.0.0.0' or 'localhost').
        port: TCP port to listen on.
    """

    host: str = Field(
        alias="UVICORN_HOST",
        default="0.0.0.0",
        description="Interface to bind the server to (e.g., '0.0.0.0' or 'localhost').",
        validate_default=True,
    )
    port: int = Field(
        alias="UVICORN_PORT",
        default=8080,
        description="TCP port to listen on.",
        validate_default=True,
    )
    fastapi_debug: bool = Field(
        alias="FASTAPI_DEBUG",
        default=True,
        description="Enable fastapi debug output.",
        validate_default=True,
    )
    allow_credentials: bool = Field(
        alias="FASTAPI_ALLOW_CREDENTIALS",
        default=False,
        description="Enable fastapi allow credentials.",
        validate_default=True,
    )
    allow_methods: list[str] = ["GET", "POST", "PUT", "PATCH", "DELETE"]
    allow_headers: list[str] = ["Authorization", "Content-Type"]


class Configs(BaseModel):
    """Aggregate configuration container for all application settings.

    Groups together all configuration components needed by the application.
    """
    asgi: ASGIConfig = Field(
        default_factory=lambda: ASGIConfig(**os.environ),
        description="ASGI configuration.",
    )
    logging: LoggingConfig = Field(
        default_factory=lambda: LoggingConfig(**os.environ),
        description="Logging configuration.",
    )
    redis: RedisConfig = Field(
        default_factory=lambda: RedisConfig(**os.environ),
        description="Redis configuration.",
    )
    genai: GenAPIConfig = Field(
        default_factory=lambda: GenAPIConfig(**os.environ),
        description="GenAI configuration.",
    )
