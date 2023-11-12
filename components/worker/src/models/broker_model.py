import uuid

from .base import BaseOrjsonModel


class QueueMessage(BaseOrjsonModel):
    """Модель сообщения для брокера."""

    notification_id: uuid.UUID
