from loguru import logger

import aiormq
from broker.rabbit import rabbit_rep


connection: aiormq.Connection | None = None
channel: aiormq.Channel | None = None


async def on_startup(host):
    global connection
    global channel
    try:
        connection = await aiormq.connect('amqp://guest:guest@127.0.0.1:5672/')
        channel = await connection.channel()

        rabbit_rep.rabbit_repository = rabbit_rep.RabbitRepository(connection, channel)

        logger.info('Connected to Rabbit successfully.')
    except Exception as er:
        logger.exception(f'Error connecting to Rabbit: {er}')


async def on_shutdown() -> None:
    if channel:
        await channel.close()
    if connection:
        await connection.close()
        logger.info('Disconnected from Rabbit.')
