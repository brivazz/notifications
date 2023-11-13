"""Реализация AbstractDB для MongoDB."""

from core.config import settings
from db.abstract import AbstractDB
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ReturnDocument
from pymongo.collection import Collection, InsertOneResult, UpdateResult
from pymongo.errors import DuplicateKeyError


class MongoDB(AbstractDB):
    """Реализация AbstractDB для взаимодействия с коллекциями MongoDB."""

    def __init__(self, db_client: AsyncIOMotorClient) -> None:
        """Конструктор класса."""
        self._mongo_client: AsyncIOMotorClient = db_client
        self.database = self._mongo_client[settings.mongo_db]

    async def get_collection(self, collection_name: str) -> Collection:
        """Получить коллекцию по названию."""
        return self.database[collection_name]

    async def save(self, collection_name: str, document: dict) -> InsertOneResult | None:
        """Создание документа в коллекции."""
        collection = await self.get_collection(collection_name)
        try:
            result: InsertOneResult = await collection.insert_one(document)
            return result.inserted_id
        except DuplicateKeyError as err:
            logger.info(err)

    async def find_one(self, collection_name: str, query: dict) -> dict | None:
        """Выборка одного документа из коллекции."""
        collection = await self.get_collection(collection_name)
        try:
            return await collection.find_one(query)  # type: ignore[no-any-return]
        except Exception as er:
            logger.exception(f'Error when searching for an entry in the {collection_name}: {er}')

    async def update_one(self, collection_name: str, query: dict, update_data: dict) -> ReturnDocument:
        """Обновление документа в коллекции."""
        collection = await self.get_collection(collection_name)
        update_result: UpdateResult = await collection.find_one_and_update(
            query,
            {'$set': update_data},
            return_document=ReturnDocument.AFTER,
        )
        return update_result
