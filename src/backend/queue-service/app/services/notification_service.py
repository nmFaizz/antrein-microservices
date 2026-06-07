from app.clients.notification_dispatcher import NotificationDispatcher
from app.clients.user_service import CustomerContact, UserServiceClient
from app.models.enums import NotificationStatus, NotificationType
from app.models.queue import Queue
from app.models.queue_notification import QueueNotification
from app.repositories.queue_notification import QueueNotificationRepository

_MESSAGES: dict[NotificationType, str] = {
    NotificationType.CONFIRMATION: (
        "Hi {name}, your queue number is {number}. We'll notify you as your "
        "turn approaches."
    ),
    NotificationType.PREPARE: (
        "Hi {name}, queue {number} — please get ready, you're 3 spots away."
    ),
    NotificationType.ALMOST: (
        "Hi {name}, queue {number} — you're almost up, please head over."
    ),
    NotificationType.CALLED: (
        "Hi {name}, queue {number} is now being called. Please proceed."
    ),
    NotificationType.SKIPPED: (
        "Hi {name}, queue {number} was skipped. Please contact our staff."
    ),
    NotificationType.REQUEUED: (
        "Hi {name}, you've been re-queued with number {number}."
    ),
}


class NotificationService:
    """Builds, persists, and dispatches customer notifications."""

    def __init__(
        self,
        notification_repo: QueueNotificationRepository,
        user_client: UserServiceClient,
        dispatcher: NotificationDispatcher,
    ) -> None:
        self.notification_repo = notification_repo
        self.user_client = user_client
        self.dispatcher = dispatcher

    def create_and_dispatch(
        self, queue: Queue, notification_type: NotificationType
    ) -> QueueNotification:
        contact = self.user_client.get_contact(queue.user_id)
        notification = QueueNotification(
            name=notification_type.value,
            queue_id=queue.id,
            customer_id=queue.user_id,
            notification_type=notification_type,
            status=NotificationStatus.PENDING,
            message=self._build_message(notification_type, queue, contact),
        )
        # Dispatcher mutates status -> sent/failed; we persist either way.
        self.dispatcher.send(notification)
        self.notification_repo.add(notification)
        return notification

    @staticmethod
    def _build_message(
        notification_type: NotificationType,
        queue: Queue,
        contact: CustomerContact,
    ) -> str:
        template = _MESSAGES.get(
            notification_type, "Hi {name}, an update on queue {number}."
        )
        return template.format(name=contact.name, number=queue.queue_number)
