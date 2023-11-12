"""API для отправки неотложных уведомлений."""

from fastapi import Depends, Body, HTTPException, status, APIRouter, Response

from service.notifications import Notifications, get_notification_service
from models.notifications import Event, NotificationError
from models.templates import Template, TemplateError
from .schemas.response_model import ResponseNotification, ResponseTemplate


events_router = APIRouter()


@events_router.post(
    '/',
    summary='Создать уведомление',
    description='Создаёт и добавляет уведомление в очередь на отправку',
    status_code=status.HTTP_201_CREATED,
    response_model=ResponseNotification
)
async def create_notification(
        event: Event = Body(),
        notification: Notifications = Depends(get_notification_service)
):
    """Создания уведомления."""
    try:
        result =  await notification.create_notification(event)
        return ResponseNotification.model_validate(result)
    except NotificationError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(err)
        ) from err


@events_router.post(
    '/template',
    summary='Создать шаблон',
    description='Создает шаблон, используемый для отправки уведомлений.',
    status_code=status.HTTP_201_CREATED,
    response_model=ResponseTemplate,
)
async def create(
        template: Template = Body(),
        # db: AbstractDBManager = Depends(get_db_manager)
        notification: Notifications = Depends(get_notification_service)
):
    """Создание шаблона."""
    try:
        result =  await notification.create_template(template)
        return ResponseTemplate.model_validate(result)
    except TemplateError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(err)
        ) from err
