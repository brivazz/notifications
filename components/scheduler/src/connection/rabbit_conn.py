import aiormq
from loguru import logger
from broker import rabbitmq


connection: aiormq.Connection | None = None
channel: aiormq.Channel | None = None


async def rabbit_conn(rabbit_host):
    global connection
    global channel
    try:
        connection = await aiormq.connect(rabbit_host)
        channel = await connection.channel()

        rabbitmq.rabbit_publisher = rabbitmq.RabbitPublisher(connection, channel)

        logger.info('Connected to Rabbit successfully.')
    except Exception as er:
        logger.exception(f'Error connecting to Rabbit: {er}')


async def close_rabbit_conn():
    if connection:
        await connection.close()
        logger.info('Disconnected from Rabbit.')
