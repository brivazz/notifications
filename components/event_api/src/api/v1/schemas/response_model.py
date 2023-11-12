import uuid
import datetime

from models.base import BaseOrjsonModel


class ResponseNotification(BaseOrjsonModel):

    event_type: str | None
    notification_type: str
    content_id: uuid.UUID | None
    content_data: str
    template_id: uuid.UUID | None
    users_ids: list[uuid.UUID]
    scheduled: bool
    cron: str | None
    scheduled_timestamp: int | None
    notification_id: uuid.UUID
    notification_time_create: datetime.datetime
    notification_status: str
    last_update: datetime.datetime
    last_notification_send: datetime.datetime | None


class ResponseTemplate(BaseOrjsonModel):
    template_id: uuid.UUID
    event_type: str | None
    notification_type: str
    subject: str | None
    content_data: str
