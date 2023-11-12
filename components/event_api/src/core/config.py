"""Настройки приложения."""

from pathlib import Path
from dotenv import load_dotenv
from pydantic import Field#BaseModel
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    """Настройки приложения."""

    project_name: str = Field('notifications')
    debug: str = Field('False')

    sentry_dsn: str = Field('https://sentry.io')
    sentry_traces_sample_rate: float = Field(1.0)
    auth_server_url: str = Field('http://nginx/api/v1/auth')

    # mongo_uri: str = 'mongodb://127.0.0.1:27017/'
    mongo_db: str = Field('notifications')
    mongo_username: str = Field('root')
    mongo_password: str = Field('example')
    mongo_host: str = Field('localhost')
    mongo_port: int = Field(27017)

    rabbit_uri: str = 'amqp://guest:guest@127.0.0.1:5672/'
    rabbit_exchange: str = 'notifications'

    notification_high_priority: int = 100
    
    base_dir: Path = Path(__file__).resolve().parent.parent

    # logging: Logging = Logging()

    # class Config:
    #     env_nested_delimiter = '__'


settings = Settings()
