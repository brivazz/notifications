"""Главный модуль сервиса Worker."""

import asyncio
import contextlib

from connection.conn import connection
from core.config import settings
from services.assistants.mail import MailMessage
from services.sender.sender_mail import get_sender
from services.worker import Worker


async def main() -> None:
    """Выполняет необходимые действия при запуске/остановке приложения."""
    db, broker = await connection()

    email_sender = await get_sender(settings.sender)
    email_message = MailMessage(email_sender)

    worker = Worker(db, broker, email_message)

    await broker.consume(settings.queue_instant, worker.on_message)
    await broker.consume(settings.queue_from_scheduler, worker.on_scheduler)

    try:
        await asyncio.Future()
    finally:
        await db.close()
        await broker.close()


if __name__ == '__main__':
    with contextlib.suppress(KeyboardInterrupt, SystemExit):
        asyncio.run(main())
