"""Репозиторий для взаимодействия с MongoDB."""

from core.config import settings
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCursor
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError
from pymongo.collection import InsertOneResult, UpdateResult

from pymongo import MongoClient
from pymongo import InsertOne
from pymongo.errors import ServerSelectionTimeoutError
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.operations import InsertOne
from typing import Any, Dict, List
import bson


class MongoRepository:
    """Класс для взаимодействия с коллекциями MongoDB."""

    def __init__(self, db_client: AsyncIOMotorClient) -> None:
        """Инициализирует экземпляр класса MongoRepository."""
        self._mongo_client: AsyncIOMotorClient = db_client
        self.database = self._mongo_client[settings.mongo_db]

    async def get_collection(self, collection_name: str) -> Collection:
        return self.database[collection_name]

    async def save(self, collection_name: str, document: dict) -> InsertOneResult:
        """Создание записи в БД."""
        collection = await self.get_collection(collection_name)
        try:
            result: InsertOneResult = await collection.insert_one(document)
            return result.inserted_id
        except DuplicateKeyError as err:
            logger.info(err)

    async def find_one(self, collection_name: str, query: dict):
        """Выборка одного документа из БД."""
        collection = await self.get_collection(collection_name)
        try:
            return await collection.find_one(query)  # type: ignore[no-any-return]
        except Exception as er:
            logger.exception(f'Error when searching for an entry in the {collection_name}: {er}')
            return

    async def update_one(self, collection_name: str, query: dict, update_data: dict):
        collection = await self.get_collection(collection_name)
        update_result: UpdateResult = await collection.find_one_and_update(
            query,
            {'$set': update_data},
            return_document=ReturnDocument.AFTER,
        )
        return update_result


mongo_repository: MongoRepository | None = None


def get_mongo_repository() -> MongoRepository | None:
    """Возвращает объект MongoRepository или None."""
    return mongo_repository

