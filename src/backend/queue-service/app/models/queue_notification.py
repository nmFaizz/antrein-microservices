import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel

from app.models.enums import NotificationStatus, NotificationType
from app.models.mixins import utcnow


class QueueNotification(SQLModel, table=True):
    """A notification dispatched to a customer about their queue ticket."""

    __tablename__ = "queue_notification"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: Optional[str] = Field(default=None)

    queue_id: uuid.UUID = Field(foreign_key="queue.id", index=True)
    customer_id: uuid.UUID = Field(index=True)

    notification_type: NotificationType
    status: NotificationStatus = Field(default=NotificationStatus.PENDING)

    message: Optional[str] = Field(default=None)
    sent_at: Optional[datetime] = Field(default=None)
    failed_reason: Optional[str] = Field(default=None)

    created_at: datetime = Field(default_factory=utcnow, nullable=False)
