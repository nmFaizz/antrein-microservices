from enum import Enum


class NotificationType(str, Enum):
    """Type of customer-facing queue notification."""

    CONFIRMATION = "confirmation"
    PREPARE = "prepare"
    ALMOST = "almost"
    CALLED = "called"
    SKIPPED = "skipped"
    REQUEUED = "requeued"


class NotificationStatus(str, Enum):
    """Delivery status of a queue notification."""

    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class TriggerType(str, Enum):
    """Actor/source that triggered a queue status change."""

    ADMIN = "admin"
    CUSTOMER = "customer"
    SYSTEM = "system"
