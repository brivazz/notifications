"""Модуль создания подключения/отключения соединения RabbitMQ."""

import aiormq
from broker import abstract, rabbitmq
from loguru import logger

connection: aiormq.Connection | None = None
channel: aiormq.Channel | None = None


async def rabbit_conn(rabbit_uri) -> None:
    """Устанавливает соединение с брокером сообщений."""
    global connection
    global channel
    try:
        connection = await aiormq.connect(rabbit_uri)
        channel = await connection.channel()

        abstract.broker = rabbitmq.RabbitBroker(connection, channel)

        logger.info('Connected to Rabbit successfully.')
    except Exception as er:
        logger.exception(f'Error connecting to Rabbit: {er}')
