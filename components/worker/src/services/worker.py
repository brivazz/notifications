import asyncio
import datetime
from functools import lru_cache

import aiormq
import orjson
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import Depends
from db.mongo import MongoDB, get_mongo
from broker.rabbitmq import Rabbit, get_rabbit
import uuid
from loguru import logger
from models.broker_model import QueueMessage
from broker.rabbitmq import Rabbit
from croniter import croniter
from .assistants.mail import MailMessage
from pydantic import BaseModel, Field
from models.notification import Notification
from models.templates import Template


class CronModel(BaseModel):
    current_time: datetime.datetime = datetime.datetime.now(datetime.timezone.utc)
    last_update: datetime.datetime
    last_notification_send: datetime.datetime | None
    time_of_deletion: datetime.timedelta = datetime.timedelta(days=1)
    time_difference: datetime.timedelta = Field(default=None)

    def __init__(self, **data):
        super().__init__(**data)
        self.last_update = data.get('last_update')
        self.last_notification_send = data.get('last_notification_send')
        utc_timezone = datetime.timezone.utc
        if self.last_notification_send is not None:
            self.last_notification_send = self.last_notification_send.astimezone(utc_timezone)
        self.last_update = self.last_update.astimezone(utc_timezone)
        self.time_difference = self.current_time - self.last_update

class Worker:
    def __init__(self, mongo: MongoDB, broker: Rabbit, email_message: MailMessage):
        self.mongo = mongo
        self.broker = broker
        self.email_message = email_message

    async def on_message(self, message):
        msg = QueueMessage(**orjson.loads(message.body))
        notification = await self.get_notification(msg.notification_id)
        if notification.notification_type.email:
            await self.send_email(notification)

    async def on_scheduler(self, message):
        scheduler_msg = QueueMessage(**orjson.loads(message.body))

        notification = await self.get_notification(scheduler_msg.notification_id)
        if notification.scheduled:
            if notification.cron:
                await self.cron(notification)
            if notification.scheduled_timestamp:
                await self.timestamp(notification)

    async def get_notification(self, notification_id: uuid.UUID) -> Notification:
        if notification:= await self.mongo.find_notification(notification_id):
            del notification['_id']
            return Notification.model_validate(notification)

    async def timestamp(self, notification: Notification):
        if notification.notification_type.email:
            await self.send_email(notification)

    async def cron(self, notification: Notification):
        cron_m = CronModel(
            last_update=notification.last_update,
            last_notification_send=notification.last_notification_send
        )
        # print(cron_m)
        if cron_m.time_difference < cron_m.time_of_deletion:
            print("Не удаляю cron еще не прошли сутки с момента последнего обновления сообщения")
            if cron_m.last_notification_send is None or cron_m.last_notification_send < cron_m.last_update:
                print('Отправляю сообщение...Последняя отправка была раньше последнего обновления.')
                # await self.send_notification(notification)
                if notification.notification_type.email:
                    await self.send_email(notification)
            return
        print("Удаляю cron прошло более суток с момента последнего обновления сообщения")
        await self.delete_task(notification.notification_id)
        await self.mongo.update_notification_after_send(notification.notification_id, cron=True)
        print('Cron пуст. Добавляю в remove_scheduled очередь.')

    async def delete_task(self, notification_id: uuid.UUID):
        await self.broker.send_to_rabbitmq(
            body=orjson.dumps(notification_id),
            routing_key='remove_scheduled.notification',
        )

    async def get_template(self, template_id: uuid.UUID):
        if template:= await self.mongo.find_template(template_id):
            del template['_id']
            return Template.model_validate(template)

    async def send_email(self, notification: Notification):
        users_ids = await self.mongo.check_users_settings(notification.users_ids, notification.notification_type)
        if notification.template_id:
            template = await self.get_template(notification.template_id)
            if await self.email_message.send(notification, template, users_ids):
                await self.mongo.update_notification_after_send(notification.notification_id)
                return
        await self.send_other_type_notification(notification)
        await self.mongo.update_notification_after_send(notification.notification_id)

    async def send_other_type_notification(self, notification: Notification):
        pass
