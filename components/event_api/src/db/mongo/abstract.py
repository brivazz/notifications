"""Описание интерфейса для работы с БД."""
from abc import ABC, abstractmethod


class DBManagerError(Exception):
    """Базовое исключение для ошибок в работе менеджера БД."""


class AbstractDBManager(ABC):
    """Простой менеджер для работы с БД."""

    @abstractmethod
    async def get(self, collection_name: str, query: dict, skip: int = 0, limit: int = 10):
        """Выборка списка документов из БД."""

    @abstractmethod
    async def get_one(self, collection_name: str, query: dict):
        """Выборка одного документа из БД."""

    @abstractmethod
    async def update_one(self, collection_name: str, query: dict, doc: dict):
        """Обновление одного документа в БД."""

    @abstractmethod
    async def delete_one(self, collection_name: str, query: dict):
        """Удаление документа из БД."""

    @abstractmethod
    async def delete_many(self, collection_name: str, query: dict):
        """Удаление документов из БД."""

    @abstractmethod
    async def save(self, collection_name: str, obj_data: dict):
        """Создание записи в БД.

        Args:
            collection_name: название таблицы (коллекции) БД;
            obj_data: словарь с данными для поиска.

        """
