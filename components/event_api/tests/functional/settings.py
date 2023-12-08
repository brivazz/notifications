"""Модуль конфигурации тестов для сервиса event_api."""

from pydantic import Field
from pydantic_settings import BaseSettings


class TestSettings(BaseSettings):
    """Класс, представляющий настройки приложения."""

    project_name: str = Field('notifications')
    debug: str = Field('False')
    service_url: str = Field('http://127.0.0.1:8000')

    mongo_host: str = Field('localhost')
    mongo_port: int = Field(27017)
    mongo_db: str = Field('notifications')

    rabbit_host: str = Field('localhost')
    rabbit_port: int = Field(5672)
    queue_instant: str = Field('instant.notification')
    queue_scheduled: str = Field('scheduled.notification')


test_settings = TestSettings()
