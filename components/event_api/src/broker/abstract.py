"""Описание интерфейса для работы с брокером сообщений."""

import abc


class AbstractBroker(abc.ABC):
    """Абстрактный класс для работы с брокером сообщений."""

    @abc.abstractclassmethod
    async def declare_queue(self, queue_name: str):
        """Создание очередей."""

    @abc.abstractclassmethod
    async def send_to_broker(self, routing_key: str, body: bytes, exchange: str = ''):
        """Публикация сообщения в очередь брокера."""


broker: AbstractBroker | None = None


async def get_broker() -> AbstractBroker:
    """DI для FastAPI. Получаем брокер сообщений."""
    await broker.declare_queue()
    return broker
