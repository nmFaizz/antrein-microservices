"""SQLModel table models for the queue service.

Importing this package registers every table in ``SQLModel.metadata``, which
Alembic targets for autogeneration.
"""

from app.models.enums import (
    NotificationStatus,
    NotificationType,
    TriggerType,
)
from app.models.queue import Queue
from app.models.queue_notification import QueueNotification
from app.models.queue_settings import QueueSettings
from app.models.queue_status import QueueStatus
from app.models.queue_status_log import QueueStatusLog

__all__ = [
    "NotificationStatus",
    "NotificationType",
    "TriggerType",
    "Queue",
    "QueueNotification",
    "QueueSettings",
    "QueueStatus",
    "QueueStatusLog",
]
