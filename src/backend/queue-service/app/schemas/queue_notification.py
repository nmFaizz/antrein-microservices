import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel

from app.models.enums import NotificationStatus, NotificationType


class QueueNotificationRead(SQLModel):
    id: uuid.UUID
    name: Optional[str]
    queue_id: uuid.UUID
    customer_id: uuid.UUID
    notification_type: NotificationType
    status: NotificationStatus
    message: Optional[str]
    sent_at: Optional[datetime]
    failed_reason: Optional[str]
    created_at: datetime
