from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ServerSelectionTimeoutError
from pymongo.database import Database
from loguru import logger
from db import mongo


mongo_client: AsyncIOMotorClient | None = None


async def mongo_conn(mongo_host):
    global mongo_client
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


async def close_mongo_conn():
    if mongo_client:
        mongo_client.close()
        logger.info('Disconnected from MongoDB.')
