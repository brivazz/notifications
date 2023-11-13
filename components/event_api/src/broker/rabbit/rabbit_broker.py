"""Реализация AbstractBroker для RabbitMQ."""

import aiormq
from broker.abstract import AbstractBroker
from core.config import settings


class RabbitBroker(AbstractBroker):
    """Реализация AbstractBroker для RabbitMQ."""

    def __init__(self, connection, channel) -> None:
        """Конструктор класса."""
        self.channel = channel
        self.connection = connection

    async def declare_queue(self) -> None:
        """Создание очередей."""
        await self.channel.queue_declare(queue=settings.queue_instant, durable=True)
        await self.channel.queue_declare(queue=settings.queue_scheduled, durable=True)

    async def send_to_broker(self, routing_key: str, body: bytes, exchange: str = '') -> None:
        """Публикация сообщения в очередь брокера."""
        message_properties = aiormq.spec.Basic.Properties(
            delivery_mode=2,
        )
        try:
            await self.channel.basic_publish(
                exchange=exchange,
                routing_key=routing_key,
                body=body,
                properties=message_properties,
            )
        except aiormq.exceptions.AMQPError as er:
            raise str(er) from er
