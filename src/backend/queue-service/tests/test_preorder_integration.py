import uuid

import pytest

from app.clients.notification_dispatcher import NotificationDispatcher
from app.clients.user_service import UserServiceClient
from app.repositories.queue import QueueRepository
from app.repositories.queue_notification import QueueNotificationRepository
from app.repositories.queue_settings import QueueSettingsRepository
from app.repositories.queue_status import QueueStatusRepository
from app.repositories.queue_status_log import QueueStatusLogRepository
from app.schemas.queue import (
    CallNextRequest,
    CancelRequest,
    QueueCreate,
    RequeueRequest,
    ServeRequest,
    SkipRequest,
)
from app.services.notification_service import NotificationService
from app.services.queue_service import QueueService
from app.services.status_resolver import StatusResolver


class RecordingPreorderClient:
    """Test double capturing every sync(...) call."""

    def __init__(self, preorder_data=None):
        self.calls = []
        self._preorder_data = preorder_data

    def sync(self, preorder_id, queue_snapshot, status=None):
        self.calls.append(
            {
                "preorder_id": preorder_id,
                "snapshot": queue_snapshot,
                "status": status,
            }
        )

    def get_preorder(self, preorder_id):
        return self._preorder_data


@pytest.fixture(name="recorder")
def recorder_fixture():
    return RecordingPreorderClient()


def _make_svc(session, seed_statuses, preorder_client):
    notification_repo = QueueNotificationRepository(session)
    return QueueService(
        session=session,
        queue_repo=QueueRepository(session),
        settings_repo=QueueSettingsRepository(session),
        log_repo=QueueStatusLogRepository(session),
        notification_repo=notification_repo,
        resolver=StatusResolver(QueueStatusRepository(session)),
        notification_service=NotificationService(
            notification_repo, UserServiceClient(), NotificationDispatcher()
        ),
        preorder_client=preorder_client,
    )


@pytest.fixture(name="svc")
def svc_fixture(session, seed_statuses, recorder):
    return _make_svc(session, seed_statuses, recorder)


def _create_with_preorder(svc):
    return svc.create_queue(
        QueueCreate(customer_id=uuid.uuid4(), preorder_id=uuid.uuid4())
    )


def test_create_does_not_push(svc, settings_row, recorder):
    # The preorder captures the initial snapshot from the 201 response itself.
    _create_with_preorder(svc)
    assert recorder.calls == []


def test_call_next_pushes_snapshot_no_status(svc, settings_row, recorder):
    q = _create_with_preorder(svc)
    svc.call_next(CallNextRequest(), uuid.uuid4())
    assert len(recorder.calls) == 1
    call = recorder.calls[0]
    assert call["status"] is None
    assert call["snapshot"]["status"] == "called"
    assert call["snapshot"]["id"] == str(q.id)
    assert set(call["snapshot"]) == {
        "id",
        "queue_number",
        "position",
        "estimated_time",
        "status",
    }


def test_serve_pushes_confirmed(svc, settings_row, recorder):
    q = _create_with_preorder(svc)
    svc.call_next(CallNextRequest(), uuid.uuid4())
    svc.serve(q.id, ServeRequest(), uuid.uuid4())
    assert recorder.calls[-1]["status"] == "confirmed"
    assert recorder.calls[-1]["snapshot"]["status"] == "served"


def test_cancel_pushes_cancelled(svc, settings_row, recorder):
    cust = uuid.uuid4()
    q = svc.create_queue(
        QueueCreate(customer_id=cust, preorder_id=uuid.uuid4())
    )
    svc.cancel(q.id, CancelRequest(), cust)
    assert recorder.calls[-1]["status"] == "cancelled"
    assert recorder.calls[-1]["snapshot"]["status"] == "cancelled"


def test_requeue_pushes_new_queue(svc, settings_row, recorder):
    q = _create_with_preorder(svc)
    svc.call_next(CallNextRequest(), uuid.uuid4())
    svc.skip(q.id, SkipRequest(trigger_type="admin"), uuid.uuid4())
    recorder.calls.clear()
    new_q = svc.requeue(q.id, RequeueRequest(), uuid.uuid4())
    assert len(recorder.calls) == 1
    # The pushed snapshot is the NEW queue (carrying the same preorder).
    assert recorder.calls[0]["snapshot"]["id"] == str(new_q.id)
    assert recorder.calls[0]["status"] is None


def test_no_preorder_id_skips_sync(svc, settings_row, recorder):
    # Queue created without a preorder_id must never trigger a sync.
    svc.create_queue(QueueCreate(customer_id=uuid.uuid4()))
    svc.call_next(CallNextRequest(), uuid.uuid4())
    assert recorder.calls == []


def test_list_surfaces_customer_name_from_preorder(
    session, seed_statuses, settings_row
):
    client = RecordingPreorderClient(
        preorder_data={"id": str(uuid.uuid4()), "customer_name": "budi"}
    )
    svc = _make_svc(session, seed_statuses, client)
    svc.create_queue(QueueCreate(customer_id=uuid.uuid4(), preorder_id=uuid.uuid4()))
    result = svc.list(
        queue_date=None, status_id=None, is_checked_in=None, offset=0, limit=50
    )
    assert result[0].customer_name == "budi"


def test_list_omits_customer_name_when_preorder_unavailable(
    session, seed_statuses, settings_row
):
    svc = _make_svc(session, seed_statuses, RecordingPreorderClient())
    svc.create_queue(QueueCreate(customer_id=uuid.uuid4(), preorder_id=uuid.uuid4()))
    result = svc.list(
        queue_date=None, status_id=None, is_checked_in=None, offset=0, limit=50
    )
    assert result[0].customer_name is None
