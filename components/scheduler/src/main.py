import asyncio
import contextlib

from connection import rabbit_conn, mongo_conn
from connection.all import conn
from services.scheduler import Scheduler
from services.scheduler_job import SchedulerJob
from auth.fake_user import User

async def main():
    await mongo_conn.mongo_conn('localhost:27017')
    await rabbit_conn.rabbit_conn('amqp://guest:guest@127.0.0.1:5672/')
    mongo, broker = await conn()

    # print(dir(rabbit_publisher))
    user = User()
    scheduler_job = SchedulerJob(broker.send_to_rabbitmq)

    scheduler = Scheduler(mongo, scheduler_job, user)
    await scheduler.download_scheduled_notifications()

    await broker.consume('scheduled.notification', scheduler.incoming)
    await broker.consume('remove_scheduled.notification', scheduler.remove)

    try:
        while True:
            await asyncio.sleep(0.1)
    finally:
        await mongo_conn.close_mongo_conn()
        await rabbit_conn.close_rabbit_conn()


if __name__ == '__main__':
    with contextlib.suppress(KeyboardInterrupt, SystemExit):
        asyncio.run(main())
