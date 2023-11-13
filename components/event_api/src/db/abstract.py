"""Описание интерфейса для работы с БД."""

import abc


class AbstractDB(abc.ABC):
    """Абстрактный класс для работы с БД."""

    @abc.abstractmethod
    async def get_collection(self, collection_name: str):
        """Получить коллекцию по названию."""

    @abc.abstractmethod
    async def save(self, collection_name: str, document: dict):
        """Создание документа в коллекции."""

    @abc.abstractmethod
    async def find_one(self, collection_name: str, query: dict):
        """Выборка одного документа из коллекции."""

    @abc.abstractmethod
    async def update_one(self, collection_name: str, query: dict, update_data: dict):
        """Обновление документа в коллекции."""


db: AbstractDB | None = None


def get_db() -> AbstractDB | None:
    """DI для FastAPI. Получаем DB."""
    return db
