"""Сервис управления уведомлениями."""

# import logging
from functools import lru_cache
from uuid import UUID

from fastapi import Depends

from core.config import settings
from db.mongo.mongo_rep import MongoRepository
from broker.rabbit.rabbit_rep import RabbitRepository
# from db.managers.abstract import AbstractDBManager, AbstractBrokerManager, DBManagerError

from db.mongo.mongo_rep import get_mongo_repository
from broker.rabbit.rabbit_rep import get_rabbit_repository
from models.notifications import (
    Event, Notification, NotificationError,
    QueueMessage, NotificationUserSettings,
)
from models.templates import Template
import bson
import uuid
from pprint import pprint
import datetime

# import os, sys
# current = os.path.dirname(os.path.realpath(__file__))
# parent = os.path.dirname(current)
# sys.path.append(parent)
# from rabbit.broker import broker


from loguru import logger



class Notifications:
    """Класс управления уведомлениями."""

    # def __init__(self, db: AbstractDBManager, broker: AbstractBrokerManager):
    def __init__(self, db: MongoRepository, broker: RabbitRepository):
        """Инициализация объекта."""
        self.db = db
        self.broker = broker

    async def create_notification(self, event: Event):
        """Записываем в базу уведомление и отправляем в очередь."""
        if event.content_id:
            if existing_doc:= await self.find_and_update_content(event.content_id, event.content_data):
                return existing_doc
        notification = Notification(**event.model_dump())
        await self.save_user_settings(notification)
        await self.db.save('notifications', notification.model_dump())
        if notification.scheduled:
            await self.broker.send_to_rabbitmq(
                body=QueueMessage(**notification.model_dump())
                .model_dump_json()
                .encode(),
                routing_key='scheduled.notification',
            )
            return notification.model_dump()
        await self.broker.send_to_rabbitmq(
            body=QueueMessage(**notification.model_dump())
            .model_dump_json()
            .encode(),
            routing_key='instant.notification',
        )
        return notification.model_dump()

    async def save_user_settings(self, notification: Notification):
        for user_id in notification.users_ids:
            user = NotificationUserSettings(
                user_id=user_id,
                **notification.model_dump()
            )
            query = {'user_id': user.user_id, 'notification_type': user.notification_type}
            if await self.db.find_one('notification_user_settings', query):
                continue
            await self.db.save('notification_user_settings', user.model_dump())

    async def find_and_update_content(self, content_id, content_data):
        query = {'content_id': content_id}
        if existing_content:= await self.db.find_one('notifications', query):
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
        template = Template(**template.model_dump())
        await self.db.save('templates', template.model_dump())
        return template.model_dump()


@lru_cache()
def get_notification_service(
        db: MongoRepository = Depends(get_mongo_repository),
        # broker: AbstractBrokerManager = Depends(get_broker_manager),
        # broker: RabbitManager = Depends(get_broker_manager)
        broker: RabbitRepository = Depends(get_rabbit_repository)
) -> Notifications:
    """Получение сервиса для DI."""
    return Notifications(db, broker)
