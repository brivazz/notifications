"""Модуль, предназначенный для имитации общения с сервисом фильмов и получения новинок."""

from faker import Faker
from models.notification import Notification
from pydantic import BaseModel


class Content(BaseModel):
    """Модель шаблона для отправки email письма."""

    subject: str
    text: str
    film: str


class ContentFilmService:
    """Класс, имитирующий работу с сервисом фильмов."""

    def __init__(self) -> None:
        """Конструктор класса."""
        self.faker = Faker()

    async def get_content(self, notification: Notification) -> Content:
        """Возращает шаблон в соответствии с типом события."""
        fake_text = f'{self.faker.catch_phrase()} {self.faker.word()}'
        film = f'На прошедшей неделе фильм "{fake_text}" в топе просмотров!'

        header = (
            '<!DOCTYPE html><html lang="ru"><head><meta charset="utf-8"><title>Добро пожаловать!</title></head><body>'
        )
        footer = '</body></html>'
        if notification.event_type == 'registered':
            subject = 'Поздравляем с регистрацией!'
            text = (
                header
                + '<h1>Привет {{ name }}! Спасибо за регистрацию в нашем уютном кинотеатре.</h1><p> {{ content }} </p>'
                + footer
            )
            content = Content(
                subject=subject,
                text=text,
                film=film,
            )
        if notification.event_type == 'like_comment':
            subject = 'Новые лайки'
            text = (
                header
                + '<h1>Привет {{ name }}!</h1><p> Вам поставили {{ content }} лайк(-ов) на {{ content_id }} комментарий </p>'
                + footer
            )
            content = Content(
                subject=subject,
                text=text,
                film=film,
            )
        return content
