from .email_mailgun import MailgunSender
from .email_print import PrintEmailSender
from .email_sendgrid import SendGridEmailSender
from core.config import settings


async def get_sender(sender_name: str):# -> Sender:
    """Возвращает объект отправки сообщений."""
    match sender_name:
        case 'mailgun':
            MailgunSender(settings.mailgun_api_key, settings.mailgun_domain, settings.mailgun_from_email)
        case 'print':
            return PrintEmailSender(settings.sendgrid_from_email)
        case 'sendgrid':
            return SendGridEmailSender(settings.sendgrid_api_key, settings.sendgrid_from_email)
        case _:
            raise ValueError('Sender {0} not found'.format(sender_name))
