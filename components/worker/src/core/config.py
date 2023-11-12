from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    rabbitmq_host: str = Field(default='localhost')
    rabbitmq_port: int = Field(default=5672)
    rabbitmq_username: str = Field(default='admin')
    rabbitmq_password: str = Field(default='admin')

    worker_mongo_host: str = Field(default='localhost')
    worker_mongo_port: int = Field(default=27127)
    worker_mongo_db: str = Field(default='notifications')
    worker_mongo_collection_notifications: str = Field(default='notifications')

    user_preference_api_url: str = Field(default='http://user_preference_api:8001')
    mailer_panel_api_url: str = Field(default='http://mailerpanel:8000')

    sendinblue_apikey: str = Field(default='asd')
    sendinblue_email_sender: str = Field(default='asd')


class SettingsQueue(BaseSettings):
    rabbitmq_queue_send_welcome: str = Field(default='emails.send-welcome')
    rabbitmq_queue_send_like: str = Field(default='emails.send-like')
    rabbitmq_queue_send_personal_selection: str = Field(
        default='emails.send-personal_selection'
    )
    rabbitmq_queue_send_bulk_mails: str = Field(default='emails.send-bulk_mails')
    rabbitmq_queue_send_mail: str = Field(default='emails.send-mail')


settings = Settings()
settings_queue = SettingsQueue()
broker_url = (
    f'pyamqp://{settings.rabbitmq_username}:{settings.rabbitmq_password}@{settings.rabbitmq_host}:'
    f'{settings.rabbitmq_port}/'
)
value_list_queue = list(settings_queue.dict().values())

class Settings(BaseSettings):
    """Класс настроек."""

    mongo_uri: str = 'mongodb://127.0.0.1:27017/'
    mongo_db: str = 'notifications'
    rabbit_uri: str = 'amqp://guest:guest@127.0.0.1/'
    rabbit_queue: str = 'emails.send'

    auth_url: str = 'http://127.0.0.1:81/api/v1/user/'
    auth_url_list: str = 'http://127.0.0.1:81/api/v1/user/list'
    auth_authorization: str = ''

    sender: str = 'print'

    sendgrid_api_key: str = ''
    sendgrid_from_email: str = ''

    mailgun_api_key: str = ''
    mailgun_domain: str = ''
    mailgun_from_email: str = ''

    class Config:
        env_nested_delimiter = '__'


settings = Settings()
