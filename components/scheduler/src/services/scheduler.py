"""Модуль управления уведомлениями в планировщике."""

import datetime
import uuid
from zoneinfo import ZoneInfo

import orjson
from auth.fake_user import User
from db.abstract import AbstractDB
from loguru import logger
from models.scheduled_notification import (
    QueueMessage,
    QueueRemove,
    ScheduledByCron,
    ScheduledByDate,
    ScheduledNotification,
)
from services.scheduler_job import SchedulerJob
from tzlocal import get_localzone


class Scheduler:
    def __init__(self, db: AbstractDB, scheduler_job: SchedulerJob, user: User) -> None:
        """Инициализация объекта."""
        self.db = db
        self.scheduler_job = scheduler_job
        self.user = user

    async def download_scheduled_notifications(self) -> None:
        """Загрузка всех запланированных уведомлений из БД."""
        current_timestamp = datetime.datetime.now(datetime.timezone.utc).timestamp()
        query = {
            '$or': [
                {'$and': [{'scheduled': True}, {'scheduled_timestamp': {'$gt': current_timestamp}}]},
                {'$and': [{'scheduled': True}, {'cron': {'$type': 'string', '$exists': True, '$ne': ''}}]},
            ]
        }
        res_docs = await self.db.find_all('notifications', query)
        for doc in res_docs:
            await self.scheduled(ScheduledNotification(**doc))

    async def scheduled(self, scheduled_notify: ScheduledNotification) -> None:
        """Добавляет в шедулер уведомление с учетом часовых поясов пользователей."""
        users_timezones = await self.user.get_timezones(scheduled_notify.users_ids)
        timezones = {item['timezone'] for item in users_timezones}

        for timezone in timezones:
            ids_users_with_same_timezone = await self.get_user_with_timezone(timezone, users_timezones)

            if scheduled_notify.scheduled_timestamp:
                scheduled_by_date = ScheduledByDate(
                    notification_id=scheduled_notify.notification_id,
                    users_ids=ids_users_with_same_timezone,
                    timezone=timezone,
                    scheduled_timestamp=scheduled_notify.scheduled_timestamp,
                )
                await self.scheduled_by_date(scheduled_by_date)

            if scheduled_notify.cron:
                scheduled_by_cron = ScheduledByCron(
                    notification_id=scheduled_notify.notification_id,
                    users_ids=ids_users_with_same_timezone,
                    timezone=timezone,
                    cron=scheduled_notify.cron,
                )
                await self.scheduled_by_cron(scheduled_by_cron)

    async def scheduled_by_date(self, scheduled_by_date: ScheduledByDate) -> None:
        """Добавляет в шедулер уведомление по дате."""
        run_date = await self.get_run_date_local(scheduled_by_date.scheduled_timestamp, scheduled_by_date.timezone)
        if run_date.timestamp() < datetime.datetime.now().timestamp():
            logger.warning(
                'Scheduled notification {} skipped, run_date: {} current: {}'.format(
                    scheduled_by_date.notification_id, run_date, datetime.datetime.now()
                )
            )
            return
        await self.scheduler_job.add_by_date(
            task_id=scheduled_by_date.notification_id,
            run_date=run_date,
            args=(QueueMessage(**scheduled_by_date.model_dump()).model_dump_json().encode(),),
        )
        logger.info(
            'Scheduled notification {} added to scheduler with run_date: {}'.format(
                scheduled_by_date.notification_id, run_date
            )
        )

    async def scheduled_by_cron(self, scheduled_by_cron: ScheduledByCron) -> None:
        """Добавляет в шедулер уведомление по крону."""
        await self.scheduler_job.add_by_cron(
            task_id=scheduled_by_cron.notification_id,
            cron=scheduled_by_cron.cron,
            timezone=scheduled_by_cron.timezone,
            args=(QueueMessage(**scheduled_by_cron.model_dump()).model_dump_json().encode(),),
        )
        logger.info(
            'Scheduled notification {} added to scheduler with cron: {} for timezone {}'.format(
                scheduled_by_cron.notification_id, scheduled_by_cron.cron, scheduled_by_cron.timezone
            )
        )

    async def get_run_date_local(self, timestamp: int, timezone: str) -> datetime.datetime:
        """Рассчитывает локальное время выполнения уведомления для таймзоны получателя."""
        local_timezone = str(get_localzone())
        local_time = datetime.datetime.fromtimestamp(timestamp)
        dt = local_time.replace(tzinfo=ZoneInfo(key=timezone))
        dt = dt.astimezone(ZoneInfo(key=local_timezone))
        return dt

    async def get_user_with_timezone(self, timezone, users_timezones) -> list[uuid.UUID]:
        return [user['user_id'] for user in filter(lambda x: x.get('timezone') == timezone, users_timezones)]

    async def remove(self, message: dict) -> None:
        """Удаляем уведомление из планировщика."""
        msg = QueueRemove(**orjson.loads(message.body))
        await self.scheduler_job.remove(msg.notification_id)

    async def incoming(self, message: dict) -> None:
        """Получаем сообщение, загружаем из БД уведомление и ставим его в очередь."""
        msg = QueueMessage(**orjson.loads(message.body))
        doc = await self.db.find_one('notifications', {'notification_id': msg.notification_id})
        if doc is None:
            logger.error(f'Scheduled notification {msg.notification_id} not found')
            await self.scheduler_job.remove(msg.notification_id)
            return

        await self.scheduled(ScheduledNotification(**doc))
