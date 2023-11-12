"""Модели уведомлений."""

import uuid
import enum
import datetime

from pydantic import Field, validator, root_validator
from fastapi import HTTPException, status
from cron_validator import CronValidator

from .base import BaseOrjsonModel


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

class Event(BaseOrjsonModel):
    """Модель события.

    Args:
        - template_id: идентификатор html шаблона
        - users_ids: идентификаторы пользователей, которым адресовано событие
        - event_type: тип события (например, "мгновенное уведомление")
        - event_data: дополнительные данные события
        - schedule_enabled: отложенное уведомление или нет
        - scheduled_timestamp: запланированное время для отправки уведомления
    """
    event_type: EventTypeEnum | None
    notification_type: NotificationTypeEnum = NotificationTypeEnum.email
    content_id: uuid.UUID | None
    content_data: str
    template_id: uuid.UUID | None = None
    users_ids: list[uuid.UUID] = Field(..., min_items=1)
    scheduled: bool = False
    cron: str | None
    scheduled_timestamp: int | None = None

    @root_validator(skip_on_failure=True)
    def validate_fields(cls, values):
        scheduled = values.get('scheduled')
        cron = values.get('cron')
        scheduled_timestamp = int(values.get('scheduled_timestamp'))
        event_type = values.get('event_type')
        content_id = values.get('content_id')
        content_data = values.get('content_data')
        template_id = values.get('template_id')
        if not event_type and not content_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Must be one of the fields content_id or event_type',
            )
        if event_type == 'registered' and not template_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='template_id must be specified if event_type is registered',
            )
        if event_type == 'like_comment' and not scheduled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='If event_type is like_comment, set the required scheduled field to true',
            )
        if event_type == 'like_comment' and not content_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='If event_type is like_comment, set the required specify content_id',
            )
        if content_id and not content_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='If the content_id field is specified, the content_data field is required',
            )
        if scheduled:
            if not cron and not scheduled_timestamp or cron and scheduled_timestamp:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail='Must be one of the fields scheduled_timestamp or cron',
                )
            current_time = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
            if scheduled_timestamp and scheduled_timestamp < current_time:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail='The scheduled_timestamp must be greater than or equal to the current time',
                )
            if cron:
                try:
                    CronValidator.parse(cron)
                except ValueError as err:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail='Invalid field cron: {0}'.format(err),
                    ) from err
        return values

class Notification(Event):
    """Модель уведомления.

    Args:
        - notification_id: уникальный идентификатор уведомления
        - notification_type: тип уведомления (например, "email", "sms", "push")
        - notification_time_create: время создания уведомления
        - notification_status: статус уведомления (например, "отправлено", "не отправлено")
        - sent_time: время отправки уведомления
    """
    notification_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    notification_time_create: datetime.datetime = Field(
        default=datetime.datetime.now(datetime.timezone.utc)
    )
    notification_status: NotificationStatusEnum = Field(
        default=NotificationStatusEnum.not_sent
    )
    last_update: datetime.datetime = Field(
        default=datetime.datetime.now(datetime.timezone.utc)
    )
    last_notification_send: datetime.datetime | None = None

class NotificationUserSettings(BaseOrjsonModel):
    """Модель настройки уведомлений.

    Args:
        - user_id: идентификаторы пользователей
        - notification_type: тип уведомления (например, "email", "sms", "push")
        - enabled: флаг, указывающий, включены ли уведомления данного типа
                                                для указанного пользователя
    """
    user_id: uuid.UUID
    notification_type: NotificationTypeEnum = NotificationTypeEnum.email
    enabled: bool = Field(default=True)


class NotificationError(Exception):
    """Базовый класс для ошибок сервиса."""


class QueueMessage(BaseOrjsonModel):
    """Модель сообщения для брокера."""

    notification_id: uuid.UUID
    # notification_type: str

