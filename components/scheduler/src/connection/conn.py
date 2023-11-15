"""Модуль для установки соединения с базой данных и брокером сообщений."""

from broker.abstract import get_broker
from connection import mongo_conn, rabbit_conn
from core.config import settings
from db.abstract import get_db


async def connection() -> tuple:
    """Возвращает кортеж экземпляров бд и брокера."""
    await mongo_conn.mongo_conn(settings.mongo_uri)
    await rabbit_conn.rabbit_conn(settings.rabbit_uri)
    db = await get_db()
    broker = await get_broker()
    return db, broker
