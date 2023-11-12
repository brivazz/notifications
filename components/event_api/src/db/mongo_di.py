"""Модуль с функцией-провайдером для подключения к MongoDB."""

from motor.motor_asyncio import AsyncIOMotorClient

mongo: AsyncIOMotorClient | None = None


def get_mongo() -> AsyncIOMotorClient:
    """Dependency injection для подключения к MongoDB."""
    return mongo
