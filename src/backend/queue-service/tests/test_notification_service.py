import uuid
from datetime import date

from app.clients.notification_dispatcher import NotificationDispatcher
from app.clients.user_service import UserServiceClient
from app.models.enums import NotificationStatus, NotificationType
from app.models.queue import Queue
from app.repositories.queue_notification import QueueNotificationRepository
from app.services.notification_service import NotificationService


def _service(session) -> NotificationService:
    return NotificationService(
        QueueNotificationRepository(session),
        UserServiceClient(),
        NotificationDispatcher(),
    )


def _queue(status_id) -> Queue:
    return Queue(
        user_id=uuid.uuid4(),
        queue_number=7,
        queue_date=date(2026, 1, 1),
        status_id=status_id,
    )


def test_create_and_dispatch_persists_and_sends(session, seed_statuses):
    service = _service(session)
    queue = _queue(seed_statuses["waiting"])
    session.add(queue)
    session.commit()

    notification = service.create_and_dispatch(
        queue, NotificationType.CONFIRMATION
    )
    session.commit()

    assert notification.notification_type == NotificationType.CONFIRMATION
    assert notification.status == NotificationStatus.SENT
    assert notification.customer_id == queue.user_id
    # Templated message includes the queue number.
    assert "7" in notification.message
    assert notification.name == "confirmation"

    stored = QueueNotificationRepository(session).list_filtered(
        queue_id=queue.id
    )
    assert len(stored) == 1


def test_message_default_template_fallback(session, seed_statuses, monkeypatch):
    # Remove templates so the default fallback message path is used.
    import app.services.notification_service as svc_module

    monkeypatch.setattr(svc_module, "_MESSAGES", {})
    service = _service(session)
    queue = _queue(seed_statuses["waiting"])
    session.add(queue)
    session.commit()

    notification = service.create_and_dispatch(
        queue, NotificationType.CALLED
    )
    assert "7" in notification.message
