"""Модуль с настройками приложения."""


from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    """Настройки приложения."""

    project_name: str = Field('notifications')
    debug: str = Field('False')

    mongo_uri: str = Field('mongodb://127.0.0.1:27017/')
    mongo_db: str = Field('notifications')

    rabbit_uri: str = Field('amqp://guest:guest@127.0.0.1:5672/')
    queue_instant: str = Field('instant.notification')
    queue_scheduled: str = Field('scheduled.notification')


settings = Settings()
