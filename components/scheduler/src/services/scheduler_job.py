"""Модуль планировщика отложенных уведомлений."""

import logging
from datetime import datetime
from uuid import UUID

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from loguru import logger
from models.scheduled_notification import QueueMessage

# from scheduler.abstract import Scheduler


# logger = logging.getLogger(__name__)


# class PractixScheduler(Scheduler):
class SchedulerJob:
    """Класс планировщика отложенных уведомлений."""

    def __init__(self, send_to_rabbit):
        """Инициализация объекта."""
        self.scheduler = AsyncIOScheduler()
        self.scheduler.start()
        self.send_to_rabbit = send_to_rabbit
        self.exchange_name = ''#exchange_name

    async def add_by_date(self, task_id: UUID, run_date: datetime, args: tuple):
        """Добавление нотификации в планировщик по дате."""
        if self.scheduler.get_job(job_id=str(task_id)):
            self.scheduler.get_job(job_id=str(task_id)).remove()

        return self.scheduler.add_job(
            self.send_to_rabbit,
            'date',
            run_date=run_date,
            args=args,
            id=str(task_id)
        )

    async def add_by_cron(self, task_id: UUID, cron: str, timezone: str, args: tuple):
    # async def add_by_cron(self, content: dict):
        """Добавление нотификации в планировщик по крону."""

        if self.scheduler.get_job(job_id=str(task_id)):
            self.scheduler.get_job(job_id=str(task_id)).remove()

        return self.scheduler.add_job(
            self.send_to_rabbit,
            CronTrigger.from_crontab(cron, timezone=timezone),
            args=args,
            id=str(task_id)
        )

    async def remove(self, task_id: UUID):
        """Удаление нотификации из планировщика."""
        if self.scheduler.get_job(job_id=str(task_id)):
            self.scheduler.get_job(job_id=str(task_id)).remove()
            logger.info('Notification {0} removed from scheduler'.format(task_id))
            return

        logger.warning('Notification {0} not found in scheduler'.format(task_id))