import uuid

import httpx
import jwt

from app.clients import notification_dispatcher as nd_module
from app.clients import preorder_service as ps_module
from app.clients.notification_dispatcher import NotificationDispatcher
from app.clients.preorder_service import PreorderServiceClient
from app.clients.user_service import CustomerContact, UserServiceClient
from app.models.enums import NotificationStatus, NotificationType
from app.models.queue_notification import QueueNotification

# 32+ bytes to satisfy PyJWT's HS256 minimum key length.
SECRET = "test-secret-key-0123456789abcdef-xyz"


class _FakeResponse:
    def __init__(self, status_code: int, text: str = ""):
        self.status_code = status_code
        self.text = text


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


# ----------------------- PreorderServiceClient ----------------------- #
def _client(base_url="http://preorder:8000"):
    return PreorderServiceClient(
        base_url=base_url, secret_key=SECRET, service_account_id="svc-account"
    )


def test_preorder_client_noop_when_disabled(monkeypatch):
    def fail(*args, **kwargs):
        raise AssertionError("httpx must not be called when disabled")

    monkeypatch.setattr(ps_module.httpx, "patch", fail)
    client = PreorderServiceClient(
        base_url=None, secret_key=SECRET, service_account_id="svc"
    )
    client.sync(uuid.uuid4(), {"queue_number": 1})  # no exception, no call


def test_preorder_client_sync_success(monkeypatch):
    captured = {}

    def fake_patch(url, json, headers, timeout):
        captured["url"] = url
        captured["json"] = json
        captured["headers"] = headers
        return _FakeResponse(200)

    monkeypatch.setattr(ps_module.httpx, "patch", fake_patch)
    pid = uuid.uuid4()
    _client().sync(pid, {"queue_number": 5}, status="confirmed")

    assert captured["url"] == f"http://preorder:8000/preorders/{pid}"
    assert captured["json"] == {"queue": {"queue_number": 5}, "status": "confirmed"}
    token = captured["headers"]["Authorization"].removeprefix("Bearer ")
    decoded = jwt.decode(token, SECRET, algorithms=["HS256"])
    assert decoded["role"] == "admin"
    assert decoded["user_id"] == "svc-account"


def test_preorder_client_omits_status_when_none(monkeypatch):
    captured = {}
    monkeypatch.setattr(
        ps_module.httpx,
        "patch",
        lambda url, json, headers, timeout: captured.update(json=json)
        or _FakeResponse(200),
    )
    _client().sync(uuid.uuid4(), {"queue_number": 1})
    assert "status" not in captured["json"]


def test_preorder_client_http_error_swallowed(monkeypatch):
    monkeypatch.setattr(
        ps_module.httpx,
        "patch",
        lambda *args, **kwargs: _FakeResponse(409, "conflict"),
    )
    # Must not raise even on a 4xx response.
    _client().sync(uuid.uuid4(), {"queue_number": 1}, status="cancelled")


def test_preorder_client_request_error_swallowed(monkeypatch):
    def raise_err(*args, **kwargs):
        raise httpx.ConnectError("unreachable")

    monkeypatch.setattr(ps_module.httpx, "patch", raise_err)
    # Best-effort: a network error is logged, not raised.
    _client().sync(uuid.uuid4(), {"queue_number": 1})
