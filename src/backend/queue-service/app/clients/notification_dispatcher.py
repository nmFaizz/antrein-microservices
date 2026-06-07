import logging

from app.models.enums import NotificationStatus
from app.models.mixins import utcnow
from app.models.queue_notification import QueueNotification

logger = logging.getLogger(__name__)


class NotificationDispatcher:
    """Sends queue notifications to customers.

    Stub implementation: logs the notification and marks it as ``sent``.
    Mutates the passed row in place; the caller is responsible for persisting
    it. Swap in a real SMS/email/push transport later without changing the
    notification service.
    """

    def send(self, notification: QueueNotification) -> None:
        try:
            logger.info(
                "Dispatching %s notification for queue %s to customer %s: %s",
                notification.notification_type,
                notification.queue_id,
                notification.customer_id,
                notification.message,
            )
            notification.status = NotificationStatus.SENT
            notification.sent_at = utcnow()
        except Exception as exc:  # pragma: no cover - defensive
            notification.status = NotificationStatus.FAILED
            notification.failed_reason = str(exc)
