"""Модуль отправки уведомлений."""

import abc
import uuid

from models.notification import Notification
from models.templates import Template


class Message(abc.ABC):
    """Класс отправки уведомлений."""

    @abc.abstractmethod
    async def send(
        self, notification: Notification, users_ids: list[uuid.UUID], template: Template = None
    ) -> Notification:
        """Отправка уведомления."""
