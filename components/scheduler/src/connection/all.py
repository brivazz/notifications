from broker.rabbitmq import get_rabbit
from db.mongo import get_mongo


async def conn():
    mongo = await get_mongo()
    rabbit_publisher = await get_rabbit()
    return mongo, rabbit_publisher
