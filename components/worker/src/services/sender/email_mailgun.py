"""Модуль отправки сообщений через Mailgun."""

from http import HTTPStatus

import aiohttp
import backoff
from loguru import logger
from models.message import EmailModel
from services.sender.abstract import Sender, SenderError


class MailgunSender(Sender):
    """Класс отправка сообщений через Mailgun."""

    def __init__(self, api_key: str, domain: str, from_email: str) -> None:
        """Инициализация объекта."""
        self.api_key = api_key
        self.domain = domain
        self.from_email = from_email

    @backoff.on_exception(backoff.expo, (SenderError, aiohttp.ClientError))
    async def send(self, msg: EmailModel) -> None:
        """Отправка сообщения через Mailgun."""
        async with aiohttp.ClientSession() as session:
            response = await session.post(
                f'https://api.mailgun.net/v3/{self.domain}/messages',
                auth=aiohttp.BasicAuth('api', self.api_key),
                data={
                    'from': self.from_email,
                    'to': msg.to_email,
                    'subject': msg.subject,
                    'html': msg.body,
                },
            )

            if response.status != HTTPStatus.OK:
                logger.error(f'Error sending email: {await response.text()}')
                raise SenderError(f'Error sending email: {await response.text()}')

            logger.info(f'Send email send to {msg.to_email}')
