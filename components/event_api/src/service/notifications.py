"""Модуль сервиса для создания уведомлений и шаблонов."""

import datetime
from functools import lru_cache

from broker.abstract import AbstractBroker, get_broker
from db.abstract import AbstractDB, get_db
from fastapi import Depends
from models.notifications import Event, Notification, NotificationUserSettings, QueueMessage
from models.templates import Template


class Notifications:
    """Сервис для создания уведомлений и шаблонов."""

    def __init__(self, db: AbstractDB, broker: AbstractBroker):
        """Инициализация объекта."""
        self.db = db
        self.broker = broker

    async def create_notification(self, event: Event):
        """Записываем в базу уведомление и отправляем в очередь."""
        if event.content_id:
            if existing_doc := await self.find_and_update_content(event.content_id, event.content_data):
                return existing_doc
        notification = Notification(**event.model_dump())
        await self.save_user_settings(notification)
        await self.db.save('notifications', notification.model_dump())
        if notification.scheduled:
            await self.broker.send_to_broker(
                body=QueueMessage(**notification.model_dump()).model_dump_json().encode(),
                routing_key='scheduled.notification',
            )
            return notification.model_dump()
        await self.broker.send_to_broker(
            body=QueueMessage(**notification.model_dump()).model_dump_json().encode(),
            routing_key='instant.notification',
        )
        return notification.model_dump()

    async def save_user_settings(self, notification: Notification):
        """Сохраняем в базу настройки пользователя по типу уведомления."""
        for user_id in notification.users_ids:
            user = NotificationUserSettings(user_id=user_id, **notification.model_dump())
            query = {'user_id': user.user_id, 'notification_type': user.notification_type}
            if await self.db.find_one('notification_user_settings', query):
                continue
            await self.db.save('notification_user_settings', user.model_dump())

    async def find_and_update_content(self, content_id, content_data):
        """Обновляем content_data у существующего conten_id в базе."""
        query = {'content_id': content_id}
        if existing_content := await self.db.find_one('notifications', query):
            res = await self.db.update_one(
                'notifications',
                existing_content,
                {
                    'content_data': content_data,
                    'last_update': datetime.datetime.now(datetime.timezone.utc),
                },
            )
            del res['_id']
            return res
        return existing_content

    async def create_template(self, template: Template):
        """Сохраняем в базу шаблон."""
        template = Template(**template.model_dump())
        await self.db.save('templates', template.model_dump())
        return template.model_dump()


@lru_cache
def get_notification_service(
    db: AbstractDB = Depends(get_db),
    broker: AbstractBroker = Depends(get_broker),
) -> Notifications:
    """DI получения сервиса для FastAPI."""
    return Notifications(db, broker)
