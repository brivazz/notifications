"""Модели шаблонов."""

import uuid

from fastapi import HTTPException, status
from jinja2 import TemplateSyntaxError, Environment
from pydantic import BaseModel, Field, validator

from models.notifications import EventTypeEnum, NotificationTypeEnum
from .base import BaseOrjsonModel


class Template(BaseOrjsonModel):
    """Модель шаблона."""

    template_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    event_type: EventTypeEnum | None
    notification_type: NotificationTypeEnum = NotificationTypeEnum.email
    title: str
    subject: str | None
    content_data: str

    @validator('subject', always=True)
    def validate_subject(cls, subject, values):
        """Проверка корректности поля subject."""
        if values.get('notification_type') == NotificationTypeEnum.email and not subject:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Subject field is required for email type',
            )

        if subject:
            try:
                Environment().parse(subject)
            except TemplateSyntaxError as err:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail='Invalid template subject: {0}'.format(err),
                )

        return subject

    @validator('content_data')
    def validate_content(cls, content_data):
        """Проверка корректности поля content."""
        try:
            Environment().parse(content_data)
        except TemplateSyntaxError as err:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Invalid template content: {0}'.format(err),
            )

        return content_data


class TemplateError(Exception):
    """Класс для ошибок шаблона."""
