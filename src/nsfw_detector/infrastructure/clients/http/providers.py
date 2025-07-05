from typing import AsyncIterator

from aiohttp import ClientSession


async def get_client() -> AsyncIterator[ClientSession]:
    async with ClientSession() as session:
        yield session
