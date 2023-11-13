"""Модуль создания подключения/отключения соединения RabbitMQ."""

import aiormq
from broker import abstract
from broker.rabbit import rabbit_broker
from loguru import logger

connection: aiormq.Connection | None = None
channel: aiormq.Channel | None = None


async def on_startup(rabbit_uri: str) -> None:
    """Создаёт соединение c RabbitMQ."""
    global connection
    global channel
    try:
        connection = await aiormq.connect(rabbit_uri)
        channel = await connection.channel()

        abstract.broker = rabbit_broker.RabbitBroker(connection, channel)

        logger.info('Connected to Rabbit successfully.')
    except Exception as er:
        logger.exception(f'Error connecting to Rabbit: {er}')


async def on_shutdown() -> None:
    """Закрывает соединение c RabbitMQ."""
    if channel:
        await channel.close()
    if connection:
        await connection.close()
    logger.info('Disconnected from Rabbit.')
