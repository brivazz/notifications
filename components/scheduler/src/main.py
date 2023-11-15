import asyncio
import contextlib

from auth.fake_user import User
from connection.conn import connection
from core.config import settings
from services.scheduler import Scheduler
from services.scheduler_job import SchedulerJob


async def main() -> None:
    """Выполняет необходимые действия при запуске/остановке приложения."""
    db, broker = await connection()

    user = User()
    scheduler_job = SchedulerJob(broker.send_to_broker)

    scheduler = Scheduler(db, scheduler_job, user)
    await scheduler.download_scheduled_notifications()

    await broker.consume(settings.queue_scheduled, scheduler.incoming)
    await broker.consume(settings.queue_remove_scheduled, scheduler.remove)

    try:
        await asyncio.Future()
    finally:
        await db.close()
        await broker.close()


if __name__ == '__main__':
    with contextlib.suppress(KeyboardInterrupt, SystemExit):
        asyncio.run(main())
