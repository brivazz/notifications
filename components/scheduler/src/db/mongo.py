"""Реализация AbstractDB для MongoDB."""

import uuid

from core.config import settings
from db.abstract import AbstractDB
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.collection import Collection
from pymongo.database import Database


class MongoDB(AbstractDB):
    """Реализация AbstractDB для взаимодействия с коллекциями MongoDB."""

    def __init__(self, mongo_client: AsyncIOMotorClient) -> None:
        """Конструктор класса."""
        self.mongo_client = mongo_client

    async def close(self) -> None:
        """Закрывает соединени с БД."""
        if self.mongo_client:
            self.mongo_client.close()
            logger.info('Disconnected from MongoDB.')

    async def get_database(self) -> Database:
        """Получает объект базы данных."""
        return self.mongo_client[settings.mongo_db]

    async def get_collection(self, collection_name: str) -> Collection:
        """Получить коллекцию по названию."""
        database = await self.get_database()
        return database[collection_name]

    async def find_all(self, collection_name: str, query: dict) -> list[dict]:
        """Поиск документов в таблице."""
        collection = await self.get_collection(collection_name)
        return await collection.find(query).to_list(length=None)

    async def find_one(self, collection_name: str, query: dict) -> dict | None:
        """Выборка одного документа из БД."""
        collection = await self.get_collection(collection_name)
        return await collection.find_one(query)

    async def check_users_settings(self, users_ids: list[uuid.UUID], notification_type: str) -> list[uuid.UUID, None]:
        """Проверяем настройки пользователя по типу оповещения."""
        query = {'notification_type': notification_type, 'enabled': True, 'user_id': {'$in': users_ids}}
        projection = {'user_id': 1}
        user_settings = await self.get_collection('notification_user_settings')
        result = await user_settings.find(query, projection).to_list(length=None)
        users_ids = [doc['user_id'] for doc in result]
        return users_ids
