"""API для создания и отправки уведомлений."""

from api.v1.schemas.response_model import ResponseNotification, ResponseTemplate
from fastapi import APIRouter, Body, Depends, status
from models.notifications import Event
from models.templates import Template
from service.notifications import Notifications, get_notification_service

events_router = APIRouter()


@events_router.post(
    '/',
    summary='Создать уведомление',
    description='Создаёт и добавляет уведомление в очередь на отправку',
    status_code=status.HTTP_201_CREATED,
    response_model=ResponseNotification,
)
async def create_notification(event: Event = Body(), notification: Notifications = Depends(get_notification_service)):
    """Создание уведомления."""
    return await notification.create_notification(event)


@events_router.post(
    '/template',
    summary='Создать шаблон',
    description='Создает шаблон, используемый для отправки уведомлений.',
    status_code=status.HTTP_201_CREATED,
    response_model=ResponseTemplate,
)
async def create(
    template: Template = Body(),
    notification: Notifications = Depends(get_notification_service),
):
    """Создание шаблона."""
    return await notification.create_template(template)
