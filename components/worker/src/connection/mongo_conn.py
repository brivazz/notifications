from db import abstract, mongo
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ServerSelectionTimeoutError

mongo_client: AsyncIOMotorClient | None = None


async def mongo_conn(mongo_uri) -> None:
    global mongo_client
    try:
        mongo_client = AsyncIOMotorClient(
            mongo_uri,
            uuidRepresentation='standard',
        )
        abstract.db = mongo.MongoDB(mongo_client)

        logger.info('Connected to MongoDB successfully.')
    except ServerSelectionTimeoutError as er:
        logger.exception(f'Error connecting to MongoDB: {er}')
    except Exception as er:
        logger.exception(f'Error connecting to MongoDB: {er}')
