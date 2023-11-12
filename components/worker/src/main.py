import asyncio
import contextlib

# import aiormq
# import orjson
# from db import mongo_di
# from broker import rabbit_di
# from motor.motor_asyncio import AsyncIOMotorClient
from services.worker import Worker

# from broker.rabbitmq import Rabbit
# from db.mongo import MongoDB
from connection import rabbit_conn, mongo_conn
from connection.all import conn
from services.assistants.mail import MailMessage
from services.sender.sender_mail import get_sender
from core.config import settings


async def main():
    await mongo_conn.mongo_conn('localhost:27017')
    await rabbit_conn.rabbit_conn('amqp://guest:guest@127.0.0.1:5672/')
    mongo, broker = await conn()

    email_sender = await get_sender(settings.sender)
    email_message = MailMessage(email_sender)

    worker = Worker(mongo, broker, email_message)

    await broker.consume('instant.notification', worker.on_message)
    await broker.consume('send_from_scheduler.notification', worker.on_scheduler)


    try:
        while True:
            await asyncio.sleep(0.1)
    finally:
        await broker.close()


if __name__ == '__main__':
    with contextlib.suppress(KeyboardInterrupt, SystemExit):
        asyncio.run(main())
