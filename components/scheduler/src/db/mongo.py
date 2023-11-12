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

    async def find_all(self, collection_name: str, query: dict) -> list[dict]:
        """Поиск документов в таблице."""
        collection = await self.get_collection(collection_name)
        return await collection.find(query).to_list(length=None)

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

    async def find_one(self, collection_name: str, query: dict):
        """Выборка одного документа из БД."""
        collection = await self.get_collection(collection_name)
        return await collection.find_one(query)

    # async def save(self, collection_name: str, document: dict) -> InsertOneResult:
    #     """Создание записи в БД."""
    #     collection = await self.get_collection(collection_name)
    #     try:
    #         result: InsertOneResult = await collection.insert_one(document)
    #         return result.inserted_id
    #     except DuplicateKeyError as err:
    #         logger.info(err)

    # async def get_today_notify(self, event_type):
    #     collection = await self.get_collection('scheduled_notifications')
    #     current_date = datetime.datetime.now(datetime.timezone.utc).replace(
    #         hour=0, minute=0, second=0, microsecond=0
    #     )
    #     print(current_date)
    #     query = {
    #         '$and': [
    #             {'event_type': event_type},
    #             {'last_update': {
    #                 '$gte': current_date,
    #                 '$lt': current_date + datetime.timedelta(days=1)
    #             }},
    #         ]
    #     }
    #     result = await collection.find(query).to_list(length=None)
    #     print(result)
    #     print()
    #     users_ids = [doc['users_ids'] for doc in result]
    #     print(users_ids)

    # async def get_ids_from_users_settings(self, notification_type):
    #     user_settings = await self.get_collection('notification_user_settings')
    #     query = {
    #         'notification_type': notification_type,
    #         'enabled': True,
    #     }
    #     pipeline = [
    #         {'$match': query},  # Фильтрация записей по заданному условию
    #         {'$project': {'_id': 0, 'user_id': 1}}  # Исключаем поле _id, выбираем только поле user_id
    #     ]
    #     result = await user_settings.aggregate(pipeline).to_list(length=None)
    #     # print(result)
    #     users_ids = [doc['user_id'] for doc in result]
    #     # print(users_ids)
    #     return users_ids


    # async def get_notifications_for_user(self, user_id):
    #     collection = await self.get_collection('scheduled_notifications')
    #     # print(user_id)
    #     query = {
    #         'users_ids': user_id
    #     }
    #     pipeline = [
    #         {'$match': query},  # Фильтрация записей по заданному условию
    #         {'$unwind': '$users_ids'},
    #         {'$project': {
    #             '_id': 0,
    #             'users_ids': 1,
    #             'notification_id': 1,
    #             'content_id': 1,
    #             'content_data': 1,
    #             'cron': 1,
    #             'scheduled_timestamp': 1,
    #             'last_update': 1,
    #             'last_notification_send': 1
    #         }}  # Исключаем поле _id, выбираем только поле user_id
    #     ]
    #     result = await collection.aggregate(pipeline).to_list(length=None)
    #     if not result:
    #         return
    #     return result



mongo: MongoDB | None = None


async def get_mongo():
    return mongo

