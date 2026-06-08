import uuid
from datetime import date, time

import pytest

from app.lib.exceptions import (
    DailyQuotaExceeded,
    InvalidStateTransition,
    NoQueueToCall,
    OutsideOperatingHours,
    QueueClosed,
    QueueNotFound,
    SettingsNotConfigured,
)
from app.models.enums import NotificationType, TriggerType
from app.repositories.queue_status_log import QueueStatusLogRepository
from app.repositories.queue_notification import QueueNotificationRepository
from app.schemas.queue import (
    CallNextRequest,
    CancelRequest,
    QueueCreate,
    RequeueRequest,
    ServeRequest,
    SkipRequest,
)
from tests.factories import make_settings

D = date(2026, 1, 1)


def _logs(session, queue_id):
    return QueueStatusLogRepository(session).list_by_queue(queue_id)


def _notif_types(session, queue_id):
    return [
        n.notification_type
        for n in QueueNotificationRepository(session).list_filtered(
            queue_id=queue_id
        )
    ]


# ------------------------------ create ------------------------------ #
def test_create_queue_happy_path(queue_service, session, settings_row):
    result = queue_service.create_queue(
        QueueCreate(customer_id=uuid.uuid4(), preorder_id=uuid.uuid4())
    )
    assert result.status_name == "waiting"
    assert result.queue_number == 1
    assert result.estimated_time is not None
    assert result.current_position == 0

    logs = _logs(session, result.id)
    assert len(logs) == 1
    assert logs[0].new_status == "waiting"
    assert logs[0].trigger_type == TriggerType.SYSTEM
    assert NotificationType.CONFIRMATION in _notif_types(session, result.id)


def test_create_requires_settings(queue_service):
    with pytest.raises(SettingsNotConfigured):
        queue_service.create_queue(QueueCreate(customer_id=uuid.uuid4()))


def test_create_queue_closed(queue_service, session):
    session.add(make_settings(is_queue_open=False))
    session.commit()
    with pytest.raises(QueueClosed):
        queue_service.create_queue(QueueCreate(customer_id=uuid.uuid4()))


def test_create_outside_hours(queue_service, session):
    # A window in the past so "now" is outside it.
    session.add(
        make_settings(open_time=time(0, 0, 0), close_time=time(0, 0, 1))
    )
    session.commit()
    with pytest.raises(OutsideOperatingHours):
        queue_service.create_queue(QueueCreate(customer_id=uuid.uuid4()))


def test_create_no_hours_configured_ok(queue_service, session):
    # open_time/close_time None -> hours check is skipped.
    session.add(make_settings(open_time=None, close_time=None))
    session.commit()
    result = queue_service.create_queue(QueueCreate(customer_id=uuid.uuid4()))
    assert result.status_name == "waiting"


def test_create_quota_exceeded(queue_service, session):
    session.add(make_settings(max_queue_per_day=1))
    session.commit()
    queue_service.create_queue(QueueCreate(customer_id=uuid.uuid4()))
    with pytest.raises(DailyQuotaExceeded):
        queue_service.create_queue(QueueCreate(customer_id=uuid.uuid4()))


# ------------------------------ check-in ------------------------------ #
def test_check_in(queue_service, session, settings_row):
    q = queue_service.create_queue(QueueCreate(customer_id=uuid.uuid4()))
    result = queue_service.check_in(q.id)
    assert result.is_checked_in is True
    assert result.checked_in_at is not None
    logs = _logs(session, q.id)
    assert logs[-1].trigger_type == TriggerType.CUSTOMER
    assert logs[-1].notes == "Customer checked in"


def test_check_in_missing_queue(queue_service, settings_row):
    with pytest.raises(QueueNotFound):
        queue_service.check_in(uuid.uuid4())


# ------------------------------ call-next ------------------------------ #
def test_call_next_prioritizes_checked_in(queue_service, session, settings_row):
    q1 = queue_service.create_queue(QueueCreate(customer_id=uuid.uuid4()))
    q2 = queue_service.create_queue(QueueCreate(customer_id=uuid.uuid4()))
    queue_service.check_in(q2.id)
    admin = uuid.uuid4()
    called = queue_service.call_next(CallNextRequest(admin_id=admin))
    assert called.id == q2.id
    assert called.status_name == "called"
    assert called.called_by == admin
    assert NotificationType.CALLED in _notif_types(session, called.id)


def test_call_next_none_available(queue_service, settings_row):
    with pytest.raises(NoQueueToCall):
        queue_service.call_next(CallNextRequest(admin_id=uuid.uuid4()))


# ------------------------------ serve ------------------------------ #
def test_serve_and_avg_recompute(queue_service, session, settings_row):
    q = queue_service.create_queue(QueueCreate(customer_id=uuid.uuid4()))
    admin = uuid.uuid4()
    queue_service.call_next(CallNextRequest(admin_id=admin))
    served = queue_service.serve(q.id, ServeRequest(admin_id=admin))
    assert served.status_name == "served"
    assert served.served_by == admin
    logs = _logs(session, q.id)
    assert logs[-1].new_status == "served"
    # avg recomputed from the (near-zero) called->served duration -> min 1.
    assert queue_service.settings_repo.get_active().avg_serve_time_mins >= 1


def test_serve_invalid_from_waiting(queue_service, settings_row):
    q = queue_service.create_queue(QueueCreate(customer_id=uuid.uuid4()))
    with pytest.raises(InvalidStateTransition):
        queue_service.serve(q.id, ServeRequest(admin_id=uuid.uuid4()))


def test_recompute_avg_no_durations_is_noop(queue_service, settings_row):
    before = queue_service.settings_repo.get_active().avg_serve_time_mins
    # No served queues for this date -> early return, settings unchanged.
    queue_service._recompute_avg_serve_time(date(2030, 1, 1))
    assert (
        queue_service.settings_repo.get_active().avg_serve_time_mins == before
    )


# ------------------------------ skip ------------------------------ #
def test_skip_admin(queue_service, session, settings_row):
    q = queue_service.create_queue(QueueCreate(customer_id=uuid.uuid4()))
    queue_service.call_next(CallNextRequest(admin_id=uuid.uuid4()))
    admin = uuid.uuid4()
    skipped = queue_service.skip(
        q.id, SkipRequest(admin_id=admin, trigger_type=TriggerType.ADMIN, notes="no show")
    )
    assert skipped.status_name == "skipped"
    assert skipped.skipped_by == admin
    logs = _logs(session, q.id)
    assert logs[-1].trigger_type == TriggerType.ADMIN
    assert logs[-1].notes == "no show"
    assert NotificationType.SKIPPED in _notif_types(session, q.id)


def test_skip_system_trigger(queue_service, session, settings_row):
    q = queue_service.create_queue(QueueCreate(customer_id=uuid.uuid4()))
    queue_service.call_next(CallNextRequest(admin_id=uuid.uuid4()))
    skipped = queue_service.skip(
        q.id, SkipRequest(trigger_type=TriggerType.SYSTEM)
    )
    assert skipped.status_name == "skipped"
    assert _logs(session, q.id)[-1].trigger_type == TriggerType.SYSTEM


# ------------------------------ requeue ------------------------------ #
def test_requeue_creates_new_queue(queue_service, session, settings_row):
    q = queue_service.create_queue(QueueCreate(customer_id=uuid.uuid4()))
    queue_service.call_next(CallNextRequest(admin_id=uuid.uuid4()))
    queue_service.skip(q.id, SkipRequest(trigger_type=TriggerType.ADMIN))
    admin = uuid.uuid4()
    new_q = queue_service.requeue(q.id, RequeueRequest(admin_id=admin))

    assert new_q.id != q.id
    assert new_q.is_requeued is True
    assert new_q.original_queue_id == q.id
    assert new_q.status_name == "waiting"
    # Source marked re_queued.
    assert queue_service.get(q.id).status_name == "re_queued"
    assert NotificationType.REQUEUED in _notif_types(session, new_q.id)


def test_requeue_invalid_from_waiting(queue_service, settings_row):
    q = queue_service.create_queue(QueueCreate(customer_id=uuid.uuid4()))
    with pytest.raises(InvalidStateTransition):
        queue_service.requeue(q.id, RequeueRequest(admin_id=uuid.uuid4()))


# ------------------------------ cancel ------------------------------ #
def test_cancel_waiting(queue_service, session, settings_row):
    cust = uuid.uuid4()
    q = queue_service.create_queue(QueueCreate(customer_id=cust))
    cancelled = queue_service.cancel(q.id, CancelRequest(customer_id=cust))
    assert cancelled.status_name == "cancelled"
    assert cancelled.cancelled_at is not None
    assert _logs(session, q.id)[-1].trigger_type == TriggerType.CUSTOMER


def test_cancel_invalid_when_called(queue_service, settings_row):
    q = queue_service.create_queue(QueueCreate(customer_id=uuid.uuid4()))
    queue_service.call_next(CallNextRequest(admin_id=uuid.uuid4()))
    with pytest.raises(InvalidStateTransition):
        queue_service.cancel(q.id, CancelRequest(customer_id=uuid.uuid4()))


# ------------------------------ reads ------------------------------ #
def test_get_and_list_with_computed_fields(queue_service, settings_row):
    q1 = queue_service.create_queue(QueueCreate(customer_id=uuid.uuid4()))
    queue_service.create_queue(QueueCreate(customer_id=uuid.uuid4()))

    got = queue_service.get(q1.id)
    assert got.current_position == 0
    assert got.estimated_wait_minutes == 0

    listed = queue_service.list(
        queue_date=None, status_id=None, is_checked_in=None, offset=0, limit=50
    )
    assert len(listed) == 2
    # Second queue is 1 behind -> wait = 1 * avg(4).
    second = next(x for x in listed if x.id != q1.id)
    assert second.current_position == 1
    assert second.estimated_wait_minutes == 4


def test_get_missing(queue_service, settings_row):
    with pytest.raises(QueueNotFound):
        queue_service.get(uuid.uuid4())


# --------------------- position notifications --------------------- #
def test_position_notifications_prepare_and_almost(queue_service, session, settings_row):
    # Create 5 waiting; first call-next removes the front, shifting positions.
    queues = [
        queue_service.create_queue(QueueCreate(customer_id=uuid.uuid4()))
        for _ in range(5)
    ]
    queue_service.call_next(CallNextRequest(admin_id=uuid.uuid4()))

    # After calling the front: remaining waiting are queues[1..4] at
    # positions 0,1,2,3 -> 'almost' at pos 1 (queues[2]), 'prepare' at pos 3 (queues[4]).
    assert NotificationType.ALMOST in _notif_types(session, queues[2].id)
    assert NotificationType.PREPARE in _notif_types(session, queues[4].id)


def test_position_notifications_dedup(queue_service, session, settings_row):
    queues = [
        queue_service.create_queue(QueueCreate(customer_id=uuid.uuid4()))
        for _ in range(5)
    ]
    queue_service.call_next(CallNextRequest(admin_id=uuid.uuid4()))
    # Serve the called one -> triggers another emit pass; no duplicate notifs.
    called = queue_service.list(
        queue_date=None, status_id=None, is_checked_in=None, offset=0, limit=50
    )
    called_q = next(x for x in called if x.status_name == "called")
    queue_service.serve(called_q.id, ServeRequest(admin_id=uuid.uuid4()))

    almost_for_q2 = [
        t for t in _notif_types(session, queues[2].id)
        if t == NotificationType.ALMOST
    ]
    assert len(almost_for_q2) == 1
