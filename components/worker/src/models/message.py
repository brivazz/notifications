"""Модуль для модели email письма."""

from pydantic import BaseModel, EmailStr


class EmailModel(BaseModel):
    """Модель для уведомления email."""

    to_email: EmailStr
    subject: str
    body: str
