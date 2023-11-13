"""Модуль отправки email сообщений."""

import abc

from models.message import EmailModel


class SenderError(Exception):
    """Базовое исключение для ошибок."""


class Sender(abc.ABC):
    """Класс отправка email сообщений."""

    @abc.abstractmethod
    async def send(self, msg: EmailModel) -> None:
        """Отправка сообщения по email."""
