"""Реализация AbstractDB для MongoDB."""

import datetime
import uuid

from core.config import settings
from db.abstract import AbstractDB
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ReturnDocument
from pymongo.collection import Collection, UpdateResult
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

    async def find_one(self, collection_name: str, query: dict) -> dict | None:
        """Выборка одного документа из БД."""
        collection = await self.get_collection(collection_name)
        return await collection.find_one(query)

    async def update_one(self, collection_name: str, query: dict, update_data: dict) -> ReturnDocument:
        """Обновление документа в коллекции."""
        collection = await self.get_collection(collection_name)
        update_result: UpdateResult = await collection.find_one_and_update(
            query,
            {'$set': update_data},
            return_document=ReturnDocument.AFTER,
        )
        return update_result

    async def update_notification_after_send(self, notification_id: uuid.UUID, cron: bool = False) -> None:
        """Обновляет запись после отправки уведомления."""
        query = {'notification_id': notification_id}
        notification = await self.find_one('notifications', query)
        if cron:
            await self.update_one('notifications', notification, {'cron': ''})
            return
        await self.update_one(
            'notifications',
            notification,
            {
                'notification_status': 'отправлено',
                'last_notification_send': datetime.datetime.now(datetime.timezone.utc),
            },
        )

    async def check_users_settings(self, users_ids: list[uuid.UUID], notification_type: str) -> list[uuid.UUID, None]:
        """Проверяем настройки пользователя по типу оповещения."""
        query = {'notification_type': notification_type, 'enabled': True, 'user_id': {'$in': users_ids}}
        projection = {'user_id': 1}
        user_settings = await self.get_collection('notification_user_settings')
        result = await user_settings.find(query, projection).to_list(length=None)
        users_ids = [doc['user_id'] for doc in result]
        return users_ids

    async def find_notification(self, notification_id: uuid.UUID) -> dict | None:
        """Поиск уведомления по id."""
        query = {'notification_id': notification_id}
        return await self.find_one('notifications', query)

    async def find_template(self, template_id: uuid.UUID) -> dict | None:
        """Поиск шаблона по id."""
        query = {'template_id': template_id}
        return await self.find_one('templates', query)
