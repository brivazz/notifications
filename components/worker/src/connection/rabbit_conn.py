import aiormq
from loguru import logger
from broker import rabbitmq


async def rabbit_conn(rabbit_host):
    try:
        connection = await aiormq.connect(rabbit_host)
        channel = await connection.channel()

        rabbitmq.rabbit_consumer = rabbitmq.Rabbit(connection, channel)

        logger.info('Connected to Rabbit successfully.')
    except Exception as er:
        logger.exception(f'Error connecting to Rabbit: {er}')
