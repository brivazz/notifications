"""Файл с моделями для запланированных уведомлений."""

import uuid

from models.base import BaseOrjsonModel
from pydantic import Field


class ScheduledNotification(BaseOrjsonModel):
    """Модель запланированного уведомления."""

    notification_id: uuid.UUID
    users_ids: list[uuid.UUID] = Field(..., min_items=1)
    cron: str | None
    scheduled_timestamp: int | None = None


class ScheduledByDate(BaseOrjsonModel):
    """Модель запланированного уведомления по дате."""

    notification_id: uuid.UUID
    users_ids: list[uuid.UUID]
    timezone: str
    scheduled_timestamp: int


class ScheduledByCron(BaseOrjsonModel):
    """Модель запланированного уведомления по крону."""

    notification_id: uuid.UUID
    users_ids: list[uuid.UUID]
    timezone: str
    cron: str


class QueueMessage(BaseOrjsonModel):
    """Модель сообщения для брокера."""

    notification_id: uuid.UUID
    users_ids: list[uuid.UUID] = None
