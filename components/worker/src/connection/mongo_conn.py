from core.config import settings
from db import abstract, mongo
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.database import Database
from pymongo.errors import ServerSelectionTimeoutError

mongo_client: AsyncIOMotorClient | None = None


async def mongo_conn(mongo_host) -> None:
    global mongo_client
    try:
        mongo_client = AsyncIOMotorClient(
            mongo_host,
            uuidRepresentation='standard',
        )
        db: Database = mongo_client[settings.mongo_db]

        abstract.db = mongo.MongoDB(db)

        logger.info('Connected to MongoDB successfully.')
    except ServerSelectionTimeoutError as er:
        logger.exception(f'Error connecting to MongoDB: {er}')
    except Exception as er:
        logger.exception(f'Error connecting to MongoDB: {er}')


async def close_mongo_conn() -> None:
    if mongo_client:
        mongo_client.close()
        logger.info('Disconnected from MongoDB.')
