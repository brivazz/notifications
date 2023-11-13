"""Модуль создания подключения/отключения к MongoDB."""

from db import abstract, mongo
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.database import Database
from pymongo.errors import ServerSelectionTimeoutError

mongo_client: AsyncIOMotorClient | None = None


async def mongo_conn(mongo_uri, mongo_db) -> None:
    """Устанавливает соединение с базой данных."""
    global mongo_client
    try:
        mongo_client = AsyncIOMotorClient(
            mongo_uri,
            uuidRepresentation='standard',
        )
        db: Database = mongo_client[mongo_db]

        abstract.db = mongo.MongoDB(db)

        logger.info('Connected to MongoDB successfully.')
    except ServerSelectionTimeoutError as er:
        logger.exception(f'Error connecting to MongoDB: {er}')
    except Exception as er:
        logger.exception(f'Error connecting to MongoDB: {er}')


async def close_mongo_conn() -> None:
    """Закрывает соединение с базой данных."""
    if mongo_client:
        mongo_client.close()
        logger.info('Disconnected from MongoDB.')
