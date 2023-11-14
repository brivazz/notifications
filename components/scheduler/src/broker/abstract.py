"""Описание интерфейса для работы с брокером сообщений."""

import abc
import typing


class AbstractBroker(abc.ABC):
    """Абстрактный класс для работы с брокером сообщений."""

    @abc.abstractclassmethod
    async def declare_queue(self) -> None:
        """Создание очередей."""

    @abc.abstractclassmethod
    async def consume(self, queue: str, callback: typing.Callable) -> None:
        """Потребитель сообщений из очереди."""

    @abc.abstractclassmethod
    async def send_to_broker(self, body: bytes, exchange: str = '') -> None:
        """Публикация сообщения в очередь брокера."""


broker: AbstractBroker | None = None


async def get_broker() -> AbstractBroker:
    await broker.declare_queue()
    return broker
