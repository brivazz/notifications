import asyncio
import datetime
from functools import lru_cache

import aiormq
import orjson
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import Depends


class Rabbit:
    def __init__(self, connection, channel):
        self.connection = connection
        self.channel = channel

    async def close(self):
        """Закрытие соединения."""
        if self.connection:
            await self.connection.close()

    async def declare_queue(self, queue_name: str=''):
        await self.channel.queue_declare(queue='send_from_scheduler.notification', durable=True)
        await self.channel.queue_declare(queue='remove_scheduled.notification', durable=True)

    async def consume(self, queue, callback):
        await self.channel.basic_consume(queue, callback, no_ack=True)

    async def send_to_rabbitmq(
        self,
        body: bytes,
        routing_key: str = '',
        exchange: str = ''
    ):
        message_properties = aiormq.spec.Basic.Properties(
            delivery_mode=2,
        )
        try:
            await self.channel.basic_publish(
                exchange=exchange,
                routing_key='remove_scheduled.notification',
                body=body,
                properties=message_properties
            )
        except aiormq.exceptions.AMQPError as er:
            raise str(er) from er


rabbit_consumer: Rabbit | None = None


async def get_rabbit():
    await rabbit_consumer.declare_queue()
    return rabbit_consumer