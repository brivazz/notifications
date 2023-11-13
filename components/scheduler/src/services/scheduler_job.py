"""Модуль планировщика отложенных уведомлений."""

import datetime
import uuid

from apscheduler import job
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from loguru import logger


class SchedulerJob:
    """Класс планировщика отложенных уведомлений."""

    def __init__(self, send_to_broker) -> None:
        """Инициализация объекта."""
        self.scheduler = AsyncIOScheduler()
        self.scheduler.start()
        self.send_to_broker = send_to_broker

    async def add_by_date(self, task_id: uuid.UUID, run_date: datetime.datetime, args: tuple) -> job.Job:
        """Добавление нотификации в планировщик по дате."""
        if self.scheduler.get_job(job_id=str(task_id)):
            self.scheduler.get_job(job_id=str(task_id)).remove()

        return self.scheduler.add_job(self.send_to_broker, 'date', run_date=run_date, args=args, id=str(task_id))

    async def add_by_cron(self, task_id: uuid.UUID, cron: str, timezone: str, args: tuple) -> job.Job:
        """Добавление нотификации в планировщик по крону."""

        if self.scheduler.get_job(job_id=str(task_id)):
            self.scheduler.get_job(job_id=str(task_id)).remove()

        return self.scheduler.add_job(
            self.send_to_broker, CronTrigger.from_crontab(cron, timezone=timezone), args=args, id=str(task_id)
        )

    async def remove(self, task_id: uuid.UUID) -> None:
        """Удаление нотификации из планировщика."""
        if self.scheduler.get_job(job_id=str(task_id)):
            self.scheduler.get_job(job_id=str(task_id)).remove()
            logger.info(f'Notification {task_id} removed from scheduler')
            return

        logger.warning(f'Notification {task_id} not found in scheduler')
