"""Реализация AbstractBroker для RabbitMQ."""

import aiormq
from broker.abstract import AbstractBroker
from core.config import settings
from loguru import logger


class RabbitBroker(AbstractBroker):
    """Реализация AbstractBroker для RabbitMQ."""

    def __init__(self, connection, channel) -> None:
        """Конструктор класса."""
        self.connection = connection
        self.channel = channel

    async def close(self) -> None:
        """Закрывает соединение с брокером."""
        if self.connection:
            await self.connection.close()
            logger.info('Disconnected from Rabbit.')

    async def declare_queue(self) -> None:
        """Создание очередей."""
        await self.channel.queue_declare(queue=settings.queue_from_scheduler, durable=True)
        await self.channel.queue_declare(queue=settings.queue_remove_scheduled, durable=True)

    async def consume(self, queue, callback):
        """Потребитель сообщений из очереди."""
        await self.channel.basic_consume(queue, callback, no_ack=True)

    async def send_to_broker(self, body: bytes, exchange: str = '') -> None:
        """Публикация сообщения в очередь брокера."""
        message_properties = aiormq.spec.Basic.Properties(
            delivery_mode=2,
        )
        try:
            await self.channel.basic_publish(
                exchange=exchange,
                routing_key=settings.queue_remove_scheduled,
                body=body,
                properties=message_properties,
            )
        except aiormq.exceptions.AMQPError as er:
            raise str(er) from er
