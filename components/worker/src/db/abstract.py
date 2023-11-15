"""Описание интерфейса для работы с БД."""

import abc
import uuid


class AbstractDB(abc.ABC):
    """Абстрактный класс для работы с БД."""

    @abc.abstractmethod
    async def close(self) -> None:
        """Закрывает соединени с БД."""

    @abc.abstractmethod
    async def get_database(self):
        """Получает объект базы данных."""

    @abc.abstractmethod
    async def get_collection(self, collection_name: str):
        """Получить коллекцию по названию."""

    @abc.abstractmethod
    async def find_one(self, collection_name: str, query: dict) -> dict | None:
        """Выборка одного документа из БД."""

    @abc.abstractmethod
    async def update_one(self, collection_name: str, query: dict, update_data: dict):
        """Обновление документа в коллекции."""

    @abc.abstractmethod
    async def update_notification_after_send(self, notification_id: uuid.UUID, cron: bool = False) -> None:
        """Обновляет запись после отправки уведомления."""

    @abc.abstractmethod
    async def check_users_settings(self, users_ids: list[uuid.UUID], notification_type: str) -> list[uuid.UUID, None]:
        """Проверяем настройки пользователя по типу оповещения."""

    @abc.abstractmethod
    async def find_notification(self, notification_id: uuid.UUID) -> dict | None:
        """Поиск уведомления по id."""

    @abc.abstractmethod
    async def find_template(self, template_id: uuid.UUID) -> dict | None:
        """Поиск шаблона по id."""


db: AbstractDB | None = None


async def get_db() -> AbstractDB:
    return db
