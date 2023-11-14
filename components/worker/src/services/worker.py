"""Модуль регулирующий отправку уведомлений."""

import uuid

import orjson
from broker.abstract import AbstractBroker
from db.abstract import AbstractDB
from loguru import logger
from models.broker_message import QueueMessage, QueueRemove
from models.notification import Notification
from models.templates import Template
from models.worker_cron import CronModel
from services.assistants.abstract import Message


class Worker:
    """Класс регулирующий отправку уведомлений."""

    def __init__(self, db: AbstractDB, broker: AbstractBroker, message: Message):
        self.db = db
        self.broker = broker
        self.message = message

    async def on_message(self, message: dict) -> None:
        """Слушает очередь мгновенных уведомлений."""
        msg = QueueMessage(**orjson.loads(message.body))
        notification = await self.get_notification(msg.notification_id)
        if notification.notification_type.email:
            await self.send_email(notification, msg.users_ids)

    async def on_scheduler(self, message: dict) -> None:
        """Слушает очередь запланированных уведомлений."""
        scheduler_msg = QueueMessage(**orjson.loads(message.body))

        notification = await self.get_notification(scheduler_msg.notification_id)
        if notification.cron:
            await self.cron(notification, scheduler_msg.users_ids)
        if notification.scheduled_timestamp:
            await self.timestamp(notification, scheduler_msg.users_ids)

    async def get_notification(self, notification_id: uuid.UUID) -> Notification | None:
        """Получает уведомление из бд по id."""
        if notification := await self.db.find_notification(notification_id):
            del notification['_id']
            return Notification.model_validate(notification)

    async def timestamp(self, notification: Notification, ids_users_with_same_timezone: list[uuid.UUID]) -> None:
        """Отправляет уведомлениен по дате отправки."""
        if notification.notification_type.email:
            await self.send_email(notification, ids_users_with_same_timezone)

    async def cron(self, notification: Notification, ids_users_with_same_timezone: list[uuid.UUID]) -> None:
        """Отправляет уведомлениен по крону."""
        cron = CronModel(
            last_update=notification.last_update, last_notification_send=notification.last_notification_send
        )
        if cron.time_difference < cron.time_of_deletion:
            if cron.last_notification_send is None or cron.last_notification_send < cron.last_update:
                if notification.notification_type.email:
                    await self.send_email(notification, ids_users_with_same_timezone)
            return
        logger.info(
            f'Удаляю cron для уведомления: "{notification.notification_id}" прошло более суток с момента последнего обновления сообщения.'
        )
        await self.delete_task(notification)
        await self.db.update_notification_after_send(notification.notification_id, cron=True)

    async def delete_task(self, notification: Notification) -> None:
        """Отправляет id уведомления в очередь для удаления из периодических оповещений по крону."""
        await self.broker.send_to_broker(body=QueueRemove(**notification.model_dump()).model_dump_json().encode())

    async def get_template(self, template_id: uuid.UUID) -> Template | None:
        """Получает уведомление из бд по id."""
        if template := await self.db.find_template(template_id):
            del template['_id']
            return Template.model_validate(template)

    async def send_email(self, notification: Notification, ids_users_with_same_timezone: list[uuid.UUID]) -> None:
        """Передаёт уведомление на отправку по email."""
        users_ids = await self.db.check_users_settings(ids_users_with_same_timezone, notification.notification_type)
        if notification.template_id:
            template = await self.get_template(notification.template_id)
        if await self.message.send(notification, users_ids, template):
            await self.db.update_notification_after_send(notification.notification_id)
