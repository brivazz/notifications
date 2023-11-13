"""Модуль с моделью для брокера."""

import uuid

from models.base import BaseOrjsonModel


class QueueMessage(BaseOrjsonModel):
    """Модель сообщения для брокера."""

    notification_id: uuid.UUID
    users_ids: list[uuid.UUID] = None
