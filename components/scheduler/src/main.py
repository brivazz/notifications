import asyncio
import contextlib

from auth.fake_user import User
from connection import mongo_conn, rabbit_conn
from connection.all import conn
from core.config import settings
from services.scheduler import Scheduler
from services.scheduler_job import SchedulerJob


async def main() -> None:
    """Главная функция запуска сервиса Scheduler."""
    await mongo_conn.mongo_conn(settings.mongo_uri, settings.mongo_db)
    await rabbit_conn.rabbit_conn(settings.rabbit_uri)
    mongo, broker = await conn()

    user = User()
    scheduler_job = SchedulerJob(broker.send_to_broker)

    scheduler = Scheduler(mongo, scheduler_job, user)
    await scheduler.download_scheduled_notifications()

    await broker.consume(settings.queue_scheduled, scheduler.incoming)
    await broker.consume(settings.queue_remove_scheduled, scheduler.remove)

    try:
        await asyncio.Future()
    finally:
        await mongo_conn.close_mongo_conn()
        await rabbit_conn.close_rabbit_conn()


if __name__ == '__main__':
    with contextlib.suppress(KeyboardInterrupt, SystemExit):
        asyncio.run(main())
