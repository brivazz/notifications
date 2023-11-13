"""Модуль с настройками приложения."""


from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    """Настройки приложения."""

    mongo_uri: str = Field('mongodb://127.0.0.1:27017/')
    mongo_db: str = Field('notifications')

    rabbit_uri: str = Field('amqp://guest:guest@127.0.0.1:5672/')
    queue_from_scheduler: str = Field('send_from_scheduler.notification')
    queue_remove_scheduled: str = Field('remove_scheduled.notification')


settings = Settings()
