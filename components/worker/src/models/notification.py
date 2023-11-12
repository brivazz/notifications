"""Модели уведомлений."""

import uuid
import enum
import datetime

from pydantic import BaseModel


class EventTypeEnum(str, enum.Enum):
    """Доступные типы события."""

    registered = 'registered'
    like_comment = 'like_comment'

class NotificationTypeEnum(str, enum.Enum):
    """Доступные типы уведомления."""

    email = 'email'

class NotificationStatusEnum(str, enum.Enum):
    """Статус уведомления."""

    shipped = 'отправлено'
    not_sent = 'не отправлено'

class Notification(BaseModel):
    """Модель уведомлений."""

    event_type: EventTypeEnum | None
    notification_type: NotificationTypeEnum = NotificationTypeEnum.email
    content_id: uuid.UUID | None
    content_data: str
    template_id: uuid.UUID | None
    users_ids: list[uuid.UUID]
    scheduled: bool = False
    cron: str | None
    scheduled_timestamp: int | None = None
    notification_id: uuid.UUID
    notification_status: NotificationStatusEnum
    last_update: datetime.datetime
    last_notification_send: datetime.datetime | None
