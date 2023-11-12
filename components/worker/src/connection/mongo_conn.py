from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ServerSelectionTimeoutError
from pymongo.database import Database
from loguru import logger
from db import mongo


async def mongo_conn(mongo_host):
    try:
        mongo_client = AsyncIOMotorClient(
            mongo_host,
            uuidRepresentation="standard",
        )
        db: Database = mongo_client['notifications']

        mongo.mongo = mongo.MongoDB(db)

        logger.info('Connected to MongoDB successfully.')
    except ServerSelectionTimeoutError as er:
        logger.exception(f'Error connecting to MongoDB: {er}')
    except Exception as er:
        logger.exception(f'Error connecting to MongoDB: {er}')
