"""Модуль создания подключения/отключения к MongoDB и создание коллекций."""

import uuid

from core.config import settings
from db import abstract
from db.mongo import mongo_rep
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import ServerSelectionTimeoutError

mongo_client: AsyncIOMotorClient | None = None


async def on_startup(mongo_uri: str) -> None:
    """Выполняет необходимые операции при запуске приложения."""
    global mongo_client
    try:
        mongo_client = AsyncIOMotorClient(
            mongo_uri,
            uuidRepresentation='standard',
        )
        db: Database = mongo_client[settings.mongo_db]

        if 'notifications' not in await db.list_collection_names():
            collection: Collection = db['notifications']
            collection.create_index([('notification_id', 1, 'content_id')], unique=True)

        if 'notification_user_settings' not in await db.list_collection_names():
            collection: Collection = db['notification_user_settings']
            collection.create_index([('user_id', 1)], unique=True)

        if 'templates' not in await db.list_collection_names():
            collection: Collection = db['templates']
            collection.create_index([('template_id', 1)], unique=True)

            template_id = uuid.UUID('3fa85f64-5717-4562-b3fc-2c963f66afa6')
            template = {
                'template_id': template_id,
                'event_type': 'registered',
                'notification_type': 'email',
                'subject': 'Поздравляем с регистрацией!',
                'content_data': """
                                <!DOCTYPE html>
                                <html lang="ru">
                                <head><title>Добро пожаловать!</title></head>
                                <body>
                                <h1>Привет {{ name }}!</h1>
                                <p> {{ content }} </p>
                                </body>
                                </html>
                                """,
            }
            await collection.insert_one(template)

        abstract.db = mongo_rep.MongoDB(mongo_client)
        logger.info('Connected to MongoDB successfully.')
    except ServerSelectionTimeoutError as er:
        logger.exception(f'Error connecting to MongoDB: {er}')
    except Exception as er:
        logger.exception(f'Error connecting to MongoDB: {er}')


async def on_shutdown() -> None:
    """
    Выполняет необходимые операции при завершении работы приложения.

    Закрывает соединение с MongoDB, если оно было установлено.
    """
    if mongo_client:
        mongo_client.close()
        logger.info('Disconnected from MongoDB.')
