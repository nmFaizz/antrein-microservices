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
    def __init__(self, status_code: int, text: str = "", json_data: dict | None = None):
        self.status_code = status_code
        self.text = text
        self._json_data = json_data or {}

    def json(self):
        return self._json_data


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


# ----------------------- get_preorder ----------------------- #
def test_preorder_client_get_noop_when_disabled(monkeypatch):
    def fail(*args, **kwargs):
        raise AssertionError("httpx must not be called when disabled")

    monkeypatch.setattr(ps_module.httpx, "get", fail)
    client = PreorderServiceClient(
        base_url=None, secret_key=SECRET, service_account_id="svc"
    )
    result = client.get_preorder(uuid.uuid4())
    assert result is None


def test_preorder_client_get_success(monkeypatch):
    captured = {}

    def fake_get(url, timeout):
        captured["url"] = url
        return _FakeResponse(
            200,
            json_data={
                "data": {
                    "id": "uuid123",
                    "user_id": "user456",
                    "total_price": 50000.0,
                    "status": "pending",
                    "notes": "Pedas",
                    "created_at": "2026-06-09T00:00:00",
                    "updated_at": None,
                    "items": [],
                    "queue": {"id": "queue789"},  # Should be stripped
                }
            },
        )

    monkeypatch.setattr(ps_module.httpx, "get", fake_get)
    pid = uuid.uuid4()
    result = _client().get_preorder(pid)

    assert captured["url"] == f"http://preorder:8000/preorders/{pid}"
    assert result is not None
    assert result["id"] == "uuid123"
    assert result["total_price"] == 50000.0
    assert "queue" not in result  # Stripped!


def test_preorder_client_get_not_found(monkeypatch):
    monkeypatch.setattr(
        ps_module.httpx, "get", lambda url, timeout: _FakeResponse(404)
    )
    result = _client().get_preorder(uuid.uuid4())
    assert result is None


def test_preorder_client_get_error_swallowed(monkeypatch):
    def raise_err(*args, **kwargs):
        raise httpx.ConnectError("unreachable")

    monkeypatch.setattr(ps_module.httpx, "get", raise_err)
    result = _client().get_preorder(uuid.uuid4())
    assert result is None
