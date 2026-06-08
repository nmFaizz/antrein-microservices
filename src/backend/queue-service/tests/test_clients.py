import uuid

from app.clients import notification_dispatcher as nd_module
from app.clients.notification_dispatcher import NotificationDispatcher
from app.clients.user_service import CustomerContact, UserServiceClient
from app.models.enums import NotificationStatus, NotificationType
from app.models.queue_notification import QueueNotification


def _notification() -> QueueNotification:
    return QueueNotification(
        queue_id=uuid.uuid4(),
        customer_id=uuid.uuid4(),
        notification_type=NotificationType.CALLED,
        message="hello",
    )


def test_user_service_get_contact():
    client = UserServiceClient()
    cid = uuid.uuid4()
    contact = client.get_contact(cid)
    assert isinstance(contact, CustomerContact)
    assert contact.customer_id == cid
    assert contact.name and contact.email and contact.phone_number


def test_dispatcher_marks_sent():
    notification = _notification()
    NotificationDispatcher().send(notification)
    assert notification.status == NotificationStatus.SENT
    assert notification.sent_at is not None


def test_dispatcher_failure_branch(monkeypatch):
    # Force the try-block to raise so the except path runs.
    def boom(*args, **kwargs):
        raise RuntimeError("transport down")

    monkeypatch.setattr(nd_module.logger, "info", boom)
    notification = _notification()
    NotificationDispatcher().send(notification)
    assert notification.status == NotificationStatus.FAILED
    assert notification.failed_reason == "transport down"
