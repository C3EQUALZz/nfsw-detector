from functools import lru_cache
from typing import Final, Iterable

from aiohttp import ClientSession
from dishka import Provider, Scope
from nsfw_image_detector import NSFWDetector

from nsfw_detector.application.common.ports.images.query_gateway import ImageQueryGateway
from nsfw_detector.application.queries.images.check_image_is_nsfw import CheckImageIsNSFWQueryHandler
from nsfw_detector.infrastructure.adapters.images.cached_query_gateway import ImageCachedQueryGateway
from nsfw_detector.infrastructure.adapters.images.nsfw_detector_query_gateway import NSFWDetectorImageQueryGateway
from nsfw_detector.infrastructure.cache.providers import get_redis_pool, get_redis
from nsfw_detector.infrastructure.clients.http.base import HttpClient
from nsfw_detector.infrastructure.clients.http.impl import AioHTTPClient
from nsfw_detector.infrastructure.clients.http.providers import get_client
from nsfw_detector.setup.configs import ASGIConfig, GenAPIConfig, RedisConfig


@lru_cache(maxsize=1)
def __get_local_nsfw_factory() -> NSFWDetector:
    return NSFWDetector()


def configs_provider() -> Provider:
    """Creates a Provider for application configuration dependencies.

    Returns:
        Provider: Configured provider instance with application-level configs.
    """
    provider: Final[Provider] = Provider()
    provider.from_context(provides=ASGIConfig, scope=Scope.APP)
    provider.from_context(provides=GenAPIConfig, scope=Scope.APP)
    provider.from_context(provides=RedisConfig, scope=Scope.APP)
    return provider


def http_provider() -> Provider:
    provider: Final[Provider] = Provider(scope=Scope.REQUEST)
    provider.provide(get_client, provides=ClientSession)
    provider.provide(AioHTTPClient, provides=HttpClient)
    return provider


def gateways_provider() -> Provider:
    provider: Final[Provider] = Provider(scope=Scope.REQUEST)
    provider.provide(__get_local_nsfw_factory, provides=NSFWDetector)
    provider.provide(NSFWDetectorImageQueryGateway, provides=ImageQueryGateway)
    return provider


def cache_provider() -> Provider:
    provider: Final[Provider] = Provider(scope=Scope.REQUEST)
    provider.provide(get_redis_pool, scope=Scope.APP)
    provider.provide(get_redis)
    provider.decorate(ImageCachedQueryGateway, provides=NSFWDetectorImageQueryGateway)
    return provider


def interactors_provider() -> Provider:
    provider: Final[Provider] = Provider(scope=Scope.REQUEST)

    provider.provide_all(
        CheckImageIsNSFWQueryHandler,
    )

    return provider


def setup_providers() -> Iterable[Provider]:
    """Assembles all dependency providers for the application.

    Returns:
        Iterable[Provider]: Tuple of all configured providers.
    """
    return (
        configs_provider(),
        http_provider(),
        interactors_provider(),
        gateways_provider(),
        cache_provider()
    )
