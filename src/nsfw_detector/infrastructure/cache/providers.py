from typing import AsyncIterator

from redis import ConnectionPool
from redis.asyncio import Redis

from nsfw_detector.setup.configs import RedisConfig


async def get_redis_pool(redis_config: RedisConfig) -> ConnectionPool:
    return ConnectionPool.from_url(
        url=redis_config.url,
        max_connections=20,
        decode_responses=False,
    )

async def get_redis(connection_pool: ConnectionPool) -> AsyncIterator[Redis]:
    client: Redis = Redis.from_pool(connection_pool=connection_pool)
    try:
        yield client
    finally:
        await client.close()
