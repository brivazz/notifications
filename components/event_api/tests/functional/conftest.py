import asyncio
import os
import sys

import aiohttp
import pytest
import pytest_asyncio

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

pytest_plugins = [
    'functional.fixtures.create_mongo_data',
]


@pytest.fixture(scope='session')
def event_loop():
    """Фикстура для создания нового событийного цикла asyncio."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope='session')
async def session_client():
    """Фикстура для создания сессии клиента aiohttp."""
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest.fixture(scope='session')
def make_get_request(session_client: aiohttp.ClientSession):
    """Выполняет http запросы."""

    async def inner(
        url: str,
        method: str = 'GET',
        params: dict | None = None,
        data: dict | None = None,
        headers: dict | None = None,
    ) -> tuple[dict, int]:
        if method == 'GET':
            async with session_client.get(url, params=params, headers=headers) as response:
                message = await response.json()
                status = response.status
                return message, status

        if method == 'POST':
            async with session_client.post(url, json=data, headers=headers) as response:
                message = await response.json()
                status = response.status
                return message, status

    return inner
