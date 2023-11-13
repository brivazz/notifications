"""Описание интерфейса для работы с БД."""

import abc
import uuid


class AbstractDB(abc.ABC):
    """Абстрактный класс для работы с БД."""

    @abc.abstractmethod
    async def get_collection(self, collection_name: str):
        """Получить коллекцию по названию."""

    @abc.abstractmethod
    async def find_all(self, collection_name: str, query: dict) -> list[dict]:
        """Поиск документов в таблице."""

    @abc.abstractmethod
    async def find_one(self, collection_name: str, query: dict):
        """Выборка одного документа из коллекции."""

    @abc.abstractmethod
    async def check_users_settings(self, users_ids: list[uuid.UUID], notification_type: str) -> list[uuid.UUID, None]:
        """Проверяем настройки пользователя по типу оповещения."""


db: AbstractDB | None = None


async def get_db() -> AbstractDB:
    return db
