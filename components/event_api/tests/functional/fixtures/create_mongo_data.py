import contextlib

import motor.motor_asyncio
import pytest
from functional.settings import test_settings
from pymongo.errors import OperationFailure

COLLECTION_NAMES = [
    'notifications',
    'notification_user_settings',
    'templates',
]


@pytest.fixture(scope='session')
async def mongo_client():
    client = motor.motor_asyncio.AsyncIOMotorClient([f'{test_settings.mongo_host}:{test_settings.mongo_port}'])
    yield client
    await client.close()


@pytest.fixture(scope='session', autouse=True)
async def delete_all_mongo_data(mongo_client: motor.motor_asyncio.AsyncIOMotorClient):
    async def delete_data(client):
        db = client[test_settings.mongo_db]

        for collection_name in COLLECTION_NAMES:
            with contextlib.suppress(OperationFailure):
                collection = db[collection_name]
                await collection.delete_many({})

    await delete_data(mongo_client)
    yield
    await delete_data(mongo_client)
