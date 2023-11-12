"""Модуль отправки email уведомлений."""

import logging
import uuid

from jinja2 import Template as TemplateJinja

# from auth.abstract import Auth, AuthError
# from db.abstract import DBManager
# from message.abstarct import Message
# from models.user import User
# from models.message import EmailModel
# from models.notifications import Notification
from models.templates import Template
from models.message import EmailModel
from models.notification import Notification
from services.sender.abstract import Sender
from services.fake_services.content_data_gen import ContentFilmService, Content
from services.fake_services.email_data_gen import EmailDataGenerator
import smtplib
from email.message import EmailMessage


logger = logging.getLogger(__name__)


# class EmailMessage(Message):
class MailMessage:
    """Класс отправки email уведомлений."""

    def __init__(self, email_sender: Sender):
        """Инициализация объекта."""
        self.email_sender = email_sender
        self.user_data = EmailDataGenerator()
        self.content_data = ContentFilmService()

    async def send(self, notification: Notification, template: Template, users_ids: list[uuid.UUID]):
        """Отправка уведомления по сообщению из брокера."""

        for user_id in users_ids:
            user = await self.user_data.generate_email_data(user_id)
            content: Content = await self.content_data.get_content(notification)

            jinja_subject = TemplateJinja(content.subject)
            jinja_body = TemplateJinja(content.text)

            mail = EmailModel(
                to_email=user.email,
                subject=jinja_subject.render({'subject': f'{content.subject}'}),
                body=jinja_body.render(
                    {
                        'name': user.name,
                        'content': notification.content_data if notification.content_data else content.film,
                        'content_id': notification.content_id if notification.content_id else '',
                    }
                ),
            )
            print()
            print(mail)
            print()
            # await self.email_sender.send(mail)
            await self.local_send(mail)
        return notification

    async def local_send(self, mail):
        # python -m smtpd -n -c DebuggingServer localhost:8025
            server = smtplib.SMTP('localhost', 8025)
            message = EmailMessage()
            message["From"] = 'from@example.com'
            message["To"] = ",".join([mail.to_email])
            message["Subject"] = mail.subject
            message.set_content(mail.body)

            server.sendmail(message["From"], message["To"], message.as_string())
            server.close()
