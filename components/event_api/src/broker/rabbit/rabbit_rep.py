# """Реализация AbstractBrokerManager для RabbitMQ."""

import aiormq


# class RabbitRepository(AbstractBrokerManager):
class RabbitRepository:
    """Реализация AbstractBrokerManager для Rabbit."""

    def __init__(self, connection, channel):
        # self.rabbitmq_uri = rabbitmq_uri
        self.channel = channel
        self.connection = connection

    async def declare_queue(self, queue_name: str=''):
        await self.channel.queue_declare(queue='instant.notification', durable=True)
        await self.channel.queue_declare(queue='scheduled.notification', durable=True)


    async def send_to_rabbitmq(
        self,
        routing_key: str,
        body: bytes,
        exchange: str = ''
    ):
        message_properties = aiormq.spec.Basic.Properties(
            delivery_mode=2,
        )
        try:
            await self.channel.basic_publish(
                exchange=exchange,
                routing_key=routing_key,
                body=body,
                properties=message_properties
            )
        except aiormq.exceptions.AMQPError as er:
            raise str(er) from er
        return 'Ok'


rabbit_repository: RabbitRepository | None = None


async def get_rabbit_repository():
    await rabbit_repository.declare_queue()
    return rabbit_repository
