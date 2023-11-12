import contextlib
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCursor
from pymongo.collection import Collection
import uuid, enum, datetime
from pydantic import Field

import orjson
from pydantic import BaseModel
import typing
import smtplib
from email.message import EmailMessage
from pprint import pprint
from pymongo.errors import DuplicateKeyError
from pymongo import ReturnDocument
from pymongo.collection import InsertOneResult, UpdateResult
import uuid
from loguru import logger


class MongoDB:
    def __init__(self, database) -> None:
        self.database = database

    async def get_collection(self, collection_name: str):
        return self.database[collection_name]

    async def find_one(self, collection_name, query):
        """Выборка одного документа из БД."""
        collection = await self.get_collection(collection_name)
        return await collection.find_one(query)

    async def update_one(self, collection_name: str, query: dict, update_data: dict):
        collection = await self.get_collection(collection_name)
        update_result: UpdateResult = await collection.find_one_and_update(
            query,
            {'$set': update_data},
            return_document=ReturnDocument.AFTER,
        )
        return update_result

    async def update_notification_after_send(self, notification_id: uuid.UUID, cron: False = None):
        query = {'notification_id': notification_id}
        notification = await self.find_one('notifications', query)
        await self.update_one(
            'notifications',
            notification,
            {
                'notification_status': 'отправлено',
                'last_notification_send': datetime.datetime.now(datetime.timezone.utc)
            }
        )
        if cron:
            await self.update_one(
                'notifications', notification, {'cron': ''})

    async def check_users_settings(
        self,
        users_ids: list[uuid.UUID],
        notification_type: str
    ) -> list[uuid.UUID, None]:
        query = {
                'notification_type': notification_type,
                'enabled': True,
                'user_id': {'$in': users_ids}
        }
        projection = {'user_id': 1}
        user_settings = await self.get_collection('notification_user_settings')
        result = await user_settings.find(query, projection).to_list(length=None)
        users_ids = [doc['user_id'] for doc in result]
        return users_ids

    async def find_notification(self, notification_id: uuid.UUID):
        query = {'notification_id': notification_id}
        return await self.find_one('notifications', query)

    async def find_template(self, template_id: uuid.UUID):
        query = {'template_id': template_id}
        return await self.find_one('templates', query)


mongo: MongoDB | None = None


async def get_mongo():
    return mongo
