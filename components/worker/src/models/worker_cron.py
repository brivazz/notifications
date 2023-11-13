"""Модуль для котроля оповещений пользователей по крону."""

import datetime

from pydantic import BaseModel, Field


class CronModel(BaseModel):
    """Модель регулятор уведомлений по крону."""

    current_time: datetime.datetime = datetime.datetime.now(datetime.timezone.utc)
    last_update: datetime.datetime
    last_notification_send: datetime.datetime | None
    time_of_deletion: datetime.timedelta = datetime.timedelta(days=1)
    time_difference: datetime.timedelta = Field(default=None)

    def __init__(self, **data) -> None:
        """Конструктор класса."""
        super().__init__(**data)
        self.last_update = data.get('last_update')
        self.last_notification_send = data.get('last_notification_send')
        utc_timezone = datetime.timezone.utc
        if self.last_notification_send is not None:
            self.last_notification_send = self.last_notification_send.astimezone(utc_timezone)
        self.last_update = self.last_update.astimezone(utc_timezone)
        self.time_difference = self.current_time - self.last_update
