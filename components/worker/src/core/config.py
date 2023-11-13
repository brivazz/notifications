"""Модуль с настройками сервиса."""

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Класс настроек."""

    mongo_uri: str = Field('mongodb://127.0.0.1:27017/')
    mongo_db: str = Field('notifications')

    rabbit_uri: str = Field('amqp://guest:guest@127.0.0.1/')
    queue_instant: str = Field('instant.notification')
    queue_from_scheduler: str = Field('send_from_scheduler.notification')
    queue_remove_scheduled: str = Field('remove_scheduled.notification')

    sender: str = Field('print')

    sendgrid_api_key: str = ''
    sendgrid_from_email: str = ''

    mailgun_api_key: str = ''
    mailgun_domain: str = ''
    mailgun_from_email: str = ''


settings = Settings()
