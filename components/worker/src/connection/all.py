"""Модуль для установки соединения с базой данных и брокером сообщений."""

from broker.abstract import get_broker
from db.abstract import get_db


async def conn() -> tuple:
    """Возвращает кортеж экземпляров бд и брокера."""
    db = await get_db()
    broker = await get_broker()
    return db, broker
