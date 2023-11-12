import uuid
import enum
import datetime

from pydantic import Field, validator, root_validator
from fastapi import HTTPException, status
from cron_validator import CronValidator

from .base import BaseOrjsonModel


class NotificationTypeEnum(str, enum.Enum):
    """Доступные типы уведомления."""

    email = 'email'


class QueueMessage(BaseOrjsonModel):

    notification_id: uuid.UUID



class ScheduledNotification(BaseOrjsonModel):
    event_type: str | None
    notification_type: str
    content_id: uuid.UUID | None
    content_data: str
    template_id: uuid.UUID | None = None
    users_ids: list[uuid.UUID] = Field(..., min_items=1)
    scheduled: bool
    cron: str | None
    scheduled_timestamp: int | None = None
    notification_id: uuid.UUID
    notification_time_create: datetime.datetime
    notification_status: str
    last_update: datetime.datetime
    last_notification_send: datetime.datetime | None


class ScheduledByDate(BaseOrjsonModel):
    notification_id: uuid.UUID
    timezone: str
    scheduled_timestamp: int


class ScheduledByCron(BaseOrjsonModel):
    notification_id: uuid.UUID
    timezone: str
    cron: str


class QueueMessage(BaseOrjsonModel):
    """Модель сообщения для брокера."""

    notification_id: uuid.UUID
    # notification_type: str
    # users_ids: list[uuid.UUID]
