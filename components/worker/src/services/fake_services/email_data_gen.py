"""Модуль для генерации фейковых имён и почтовых адресов пользователей."""

import uuid

from faker import Faker
from pydantic import BaseModel, EmailStr


class EmailData(BaseModel):
    """Модель данных пользователя."""

    name: str
    email: EmailStr


class EmailDataGenerator:
    """Класс для генерации фейковых данных пользователя."""

    def __init__(self) -> None:
        self.faker = Faker()

    async def generate_email_data(self, user_id: uuid.UUID) -> EmailData:
        """Генерирует имя и почту пользователя."""
        name = self.faker.name()
        email = self.faker.email()
        return EmailData(name=name, email=email)
