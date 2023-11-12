"""Модуль управления уведомлениями в планировщике."""

import logging
import datetime
import uuid

from tzlocal import get_localzone
from zoneinfo import ZoneInfo
import asyncio
from loguru import logger
import orjson

# from auth.abstract import Auth
# from db.abstract import DBManager
# from notification.abstract import Notification
# from models.schemas import ScheduledNotification, SubScheduledNotification, BrokerMessage
# from scheduler.abstract import Scheduler
from db.mongo import MongoDB
from broker.rabbitmq import RabbitPublisher
from .scheduler_job import SchedulerJob
import json
from auth.fake_user import User
from models.scheduled_notification import (
    ScheduledNotification, ScheduledByDate,
    ScheduledByCron, QueueMessage
)

logger = logging.getLogger(__name__)


class Scheduler:
    def __init__(self, mongo: MongoDB, scheduler_job: SchedulerJob, user: User):
        """Инициализация объекта."""
        self.mongo = mongo
        self.scheduler_job = scheduler_job
        self.user = user

    # async def today_notification(self):
    #     current_date = datetime.datetime.now().date().isoformat()
    #     event_type = 'like_comment'
    #     # print(current_date)
    #     await self.mongo.get_today_notify(
    #         event_type,
    #     )

    # async def get_users_ids(self):
    #     users_ids_for_email = await self.mongo.get_user_ids_from_settings_type_notification('email')
    #     await self.get_notifications_for_user(users_ids_for_email)

    # async def get_notifications_for_user(self, users_ids):
    #     for user_id in users_ids:
    #         notifications: list[dict] = await self.mongo.get_notifications_for_user(user_id)
    #         if not notifications:
    #             continue
    #         await self.get_one_notification_user(notifications)

    # async def get_one_notification_user(self, notifications: list[dict]):
    #     for notification in notifications:
    #         print('otpravleno v cron', notification)
    #         print()
    #         """{
    #             'notification_id': UUID('d362d28a-655a-4dde-abb2-e2293eec9afb'),
    #             'content_id': UUID('3fa85f64-5717-4562-b3fc-2c963f66afa2'),
    #             'content_data': {'likes_count': 33},
    #             'users_ids': [UUID('3fa85f64-5717-4562-b3fc-2c963f66afa6')],
    #             'cron': '* * * * *',
    #             'scheduled_timestamp': None,
    #             'last_update': datetime.datetime(2023, 10, 31, 7, 24, 1, 729000),
    #             'last_notification_send': None
    #             }"""
            
    #         await self.push_in_cron_job(notification)

    # async def push_in_cron_job(self, notification: dict):
    #     await self.scheduler_job.add_cron(
    #         # TODO тут надо попробовать функцию для отправки в очередь
    #         # функцию надо создать еще
    #         # task_id=content['content_id'],
    #         # cron=content['cron'],
    #         # timezone='utc',
    #         # args=(json.dumps(content['content_data']).encode(),)
    #         # user_id,
    #         notification
    #     )

    # async def get_notify_with_timestamp(self, docs: list[dict]):
    #     # for doc in docs:
    #         # keys = [key for key, value in doc.items() if key == 'scheduled_timestamp' and value is not None and value != 0]
    #     # filtered_data_list = [
    #     #     {key: value for key, value in dictionary.items() if key == 'scheduled_timestamp' and value is not None and value != 0}
    #     #     for dictionary in docs
    #     # ]
    #     # print(filtered_data_list)
    #     filtered_data_list = [
    #         {key: value for key, value in dictionary.items() if key == 'scheduled_timestamp' and value is not None and value != 0}
    #         for dictionary in docs
    #     ]
    #     complete_data_list = [dictionary for dictionary in docs if dictionary in filtered_data_list]
    #     print(complete_data_list)

    async def download_scheduled_notifications(self):
        """Загрузка всех запланированных уведомлений из БД."""
        current_timestamp = datetime.datetime.now(datetime.timezone.utc).timestamp()
        query = {
            '$or': [
                {'$and': [{'scheduled': True}, {'scheduled_timestamp': {'$gt': current_timestamp}}]},
                {'$and': [{'scheduled': True}, {'cron': {'$type': 'string', '$exists': True, '$ne': ''}}]}
            ]
        }
        res_docs = await self.mongo.find_all('notifications', query)
        for doc in res_docs:
            await self.scheduled(ScheduledNotification(**doc))

    async def scheduled(self, scheduled_notify: ScheduledNotification):
        # users_ids = await self.mongo.check_users_settings(
        #     scheduled_notify.users_ids,
        #     scheduled_notify.notification_type
        # )
        users_timezones = await self.user.get_timezones(scheduled_notify.users_ids)
        timezones = {item['timezone'] for item in users_timezones}

        for timezone in timezones:
            ids_users_with_same_timezone = await self.get_user_with_timezone(timezone, users_timezones)

            if scheduled_notify.scheduled_timestamp:
                scheduled_by_date = ScheduledByDate(
                    notification_id=scheduled_notify.notification_id,
                    notification_type=scheduled_notify.notification_type,
                    users_ids=ids_users_with_same_timezone,
                    timezone=timezone,
                    scheduled_timestamp=scheduled_notify.scheduled_timestamp
                )
                await self.scheduled_by_date(scheduled_by_date)

            if scheduled_notify.cron:
                scheduled_by_cron = ScheduledByCron(
                    notification_id=scheduled_notify.notification_id,
                    notification_type=scheduled_notify.notification_type,
                    users_ids=ids_users_with_same_timezone,
                    timezone=timezone,
                    cron=scheduled_notify.cron
                )
                await self.scheduled_by_cron(scheduled_by_cron)

    async def scheduled_by_date(self, scheduled_by_date: ScheduledByDate):
        run_date = await self.get_run_date_local(scheduled_by_date.scheduled_timestamp, scheduled_by_date.timezone)
        if run_date.timestamp() < datetime.datetime.now().timestamp():
            logger.warning('Scheduled notification {0} skipped, run_date: {1} current: {2}'.format(
                scheduled_by_date.notification_id,
                run_date,
                datetime.datetime.now()
            ))
            return
        await self.scheduler_job.add_by_date(
            task_id=scheduled_by_date.notification_id,
            run_date=run_date,
            args=(QueueMessage(**scheduled_by_date.model_dump()).model_dump_json().encode(),)
        )
        logger.info('Scheduled notification {0} added to scheduler with run_date: {1}'.format(
            scheduled_by_date.notification_id, run_date
        ))
        print('Scheduled notification {0} added to scheduler with run_date: {1}'.format(
            scheduled_by_date.notification_id, run_date))

    async def scheduled_by_cron(self, scheduled_by_cron: ScheduledByCron):
        await self.scheduler_job.add_by_cron(
            task_id=scheduled_by_cron.notification_id,
            cron=scheduled_by_cron.cron,
            timezone=scheduled_by_cron.timezone,
            args=(QueueMessage(**scheduled_by_cron.model_dump()).model_dump_json().encode(),)
        )
        print('Scheduled notification {0} added to scheduler with cron: {1} for timezone {2}'.format(
            scheduled_by_cron.notification_id, scheduled_by_cron.cron, scheduled_by_cron.timezone))

    async def get_run_date_local(self, timestamp: int, timezone: str) -> datetime.datetime:
        """Рассчитывает локальное время выполнения уведомления для таймзоны получателя."""
        local_timezone = str(get_localzone())
        local_time = datetime.datetime.fromtimestamp(timestamp)
        dt = local_time.replace(tzinfo=ZoneInfo(key=timezone))
        dt = dt.astimezone(ZoneInfo(key=local_timezone))
        return dt

    async def get_user_with_timezone(self, timezone, users_timezones):
        return [
            user['user_id'] for user in filter(
                lambda x: x.get('timezone') == timezone, users_timezones
                )
        ]

    async def remove(self, message: dict):
        """Удаляем уведомление из планировщика."""
        notification_id = orjson.loads(message.body)
        # if 'notification_id' not in incoming_message:
        #     logger.error('Invalid incoming removing message {0}'.format(incoming_message))
        #     return
        await self.scheduler_job.remove(notification_id)

    async def incoming(self, message: dict):
        """Получаем сообщение, загружаем из БД уведомление и ставим его в очередь."""
        msg = QueueMessage(**orjson.loads(message.body))
        doc = await self.mongo.find_one('notifications', {'notification_id': msg.notification_id})
        if doc is None:
            logger.error('Scheduled notification {0} not found'.format(msg.notification_id))
            return

        await self.scheduled(ScheduledNotification(**doc))








    # async def init(self):
    #     """Загрузка запланированных уведомлений из БД и постановка их в планировщик."""
    #     query = {
    #         '$or': [
    #             {'$and': [{'enabled': True}, {'timestamp_start': {'$gt': datetime.now().timestamp()}}]},
    #             {'$and': [{'enabled': True}, {'cron': {'$type': 'string', '$exists': True, '$ne': ''}}]}
    #         ]
    #     }
    #     for notify in await self.db.find('scheduled_notifications', query):
    #         await self.scheduled(ScheduledNotification(**notify))

    # async def incoming(self, incoming_message: dict):
    #     """Получаем сообщение, загружаем из БД уведомление и ставим его в очередь."""
    #     if not isinstance(incoming_message, dict):
    #         logger.error('Invalid incoming message {0}'.format(incoming_message))
    #         return

    #     if 'notification_id' not in incoming_message:
    #         logger.error('Invalid incoming scheduling message {0}'.format(incoming_message))
    #         return

    #     notify_id = incoming_message['notification_id']
    #     if isinstance(incoming_message['notification_id'], str):
    #         notify_id = UUID(incoming_message['notification_id'])

    #     notify = await self._get_notification(notify_id)
    #     if notify is None:
    #         logger.error('Scheduled notification {0} not found'.format(notify_id))
    #         return

    #     await self.scheduled(notify)

    # async def scheduled(self, scheduled_notify: ScheduledNotification):
    #     """Разбиваем время выполнения по таймзонам и ставим на выполнение."""
    #     if not scheduled_notify.sub_notifications:
    #         scheduled_notify.sub_notifications = await self._create_sub_notifications(scheduled_notify)
    #         await self.db.update_one(
    #             'scheduled_notifications',
    #             {'scheduled_id': scheduled_notify.scheduled_id},
    #             {'sub_notifications': scheduled_notify.sub_notifications}
    #         )

    #     for notify_id, timezone in scheduled_notify.sub_notifications:
    #         if scheduled_notify.timestamp_start:
    #             await self._scheduled_by_date(scheduled_notify, notify_id, timezone)
    #             continue

    #         await self._scheduled_by_cron(scheduled_notify, notify_id, timezone)

    # async def _scheduled_by_cron(self, scheduled_notify: ScheduledNotification, notify_id: UUID, timezone: str):
    #     """Установка в планировщик периодической задачи по крону."""
    #     await self.scheduler.add_cron(
    #         task_id=notify_id,
    #         cron=scheduled_notify.cron,
    #         timezone=timezone,
    #         args=(BrokerMessage(notification_id=notify_id), '{}.send'.format(scheduled_notify.type.value))
    #     )
    #     logger.info('Scheduled notification {0} added to scheduler with cron: {1} for timezone {2}'.format(
    #         notify_id, scheduled_notify.cron, timezone
    #     ))

    # async def _scheduled_by_date(self, scheduled_notify: ScheduledNotification, notify_id: UUID, timezone: str):
    #     """Установка в планировщик задачи по дате."""
    #     run_date = await self._get_run_date_local(scheduled_notify.timestamp_start, timezone)
    #     if run_date.timestamp() < datetime.now().timestamp():
    #         logger.warning('Scheduled notification {0} skipped, run_date: {1} current: {2}'.format(
    #             notify_id,
    #             run_date,
    #             datetime.now()
    #         ))
    #         return

    #     await self.scheduler.add(
    #         task_id=notify_id,
    #         run_date=run_date,
    #         args=(BrokerMessage(notification_id=notify_id), '{}.send'.format(scheduled_notify.type.value))
    #     )
    #     logger.info('Scheduled notification {0} added to scheduler with run_date: {1}'.format(
    #         notify_id, run_date
    #     ))

    # async def remove(self, incoming_message: dict):
    #     """Удаляем уведомление из планировщика."""
    #     if 'notification_id' not in incoming_message:
    #         logger.error('Invalid incoming removing message {0}'.format(incoming_message))
    #         return

    #     await self.scheduler.remove(UUID(incoming_message['notification_id']))

    # async def _create_sub_notifications(self, notify: ScheduledNotification) -> list[tuple[UUID, str]] | None:
    #     """Создаем уведомления для разных таймзон пользователей."""
    #     result = []
    #     users_list = await self.user.get_list(notify.users)
    #     timezones = set(item['timezone'] for item in users_list)

    #     for timezone in timezones:
    #         sub_notification = SubScheduledNotification.parse_obj({
    #             **notify.dict(),
    #             'users': await self._get_user_with_timezone(users_list, timezone),
    #             'scheduled_id': notify.scheduled_id,
    #         })
    #         await self.db.insert_one('notifications', sub_notification.dict())
    #         result.append((sub_notification.notification_id, timezone))

    #     if result:
    #         return result

    #     return None

    # async def _get_notification(self, notification_id: UUID) -> ScheduledNotification | None:
    #     """Загрузка уведомления из БД."""
    #     doc = await self.db.get_one('scheduled_notifications', {'scheduled_id': notification_id, 'enabled': True})
    #     if doc:
    #         return ScheduledNotification(**doc)
    #     return None

    # @staticmethod
    # async def _get_run_date_local(timestamp: int, timezone: str) -> datetime:
    #     """Рассчитывает локальное время выполнения уведомления для таймзоны получателя."""
    #     local_timezone = str(get_localzone())
    #     dt = datetime.fromtimestamp(timestamp)
    #     dt = dt.replace(tzinfo=ZoneInfo(key=timezone))
    #     dt = dt.astimezone(ZoneInfo(key=local_timezone))

    #     return dt

    # @staticmethod
    # async def _get_user_with_timezone(users: list, timezone: str) -> list:
    #     """Возвращает список пользователей с указанной таймзоной."""
    #     users_with_timezone = []
    #     for user in filter(lambda x: x['timezone'] == timezone, users):
    #         users_with_timezone.append(user['user_id'])

    #     return users_with_timezone
