"""Модель шаблонов."""

import uuid

from models.base import BaseOrjsonModel
from models.notification import EventTypeEnum, NotificationTypeEnum
from pydantic import validator


class Template(BaseOrjsonModel):
    """Модель шаблонов."""

    template_id: uuid.UUID
    event_type: EventTypeEnum | None
    notification_type: NotificationTypeEnum = NotificationTypeEnum.email
    subject: str | None
    content_data: str

    @validator('subject', always=True)
    def validate_subject(cls, subject, values):
        """Проверка что тема сообщения заполнена для email."""
        if values.get('notification_type') == NotificationTypeEnum.email and subject is None:
            raise ValueError('Subject required for type email')
        return subject
