import uuid
from datetime import date

from app.models.enums import NotificationStatus, NotificationType, TriggerType
from app.models.queue_notification import QueueNotification
from app.models.queue_status_log import QueueStatusLog
from app.repositories.queue import QueueRepository
from app.repositories.queue_notification import QueueNotificationRepository
from app.repositories.queue_settings import QueueSettingsRepository
from app.repositories.queue_status import QueueStatusRepository
from app.repositories.queue_status_log import QueueStatusLogRepository
from tests.factories import make_queue, make_settings, utc_naive

D = date(2026, 1, 1)


# --------------------------- QueueRepository --------------------------- #
def test_next_queue_number_empty_then_increment(session, seed_statuses):
    repo = QueueRepository(session)
    assert repo.next_queue_number(D) == 1
    repo.add(make_queue(status_id=seed_statuses["waiting"], queue_number=1))
    repo.add(make_queue(status_id=seed_statuses["waiting"], queue_number=2))
    session.commit()
    assert repo.next_queue_number(D) == 3


def test_count_for_date(session, seed_statuses):
    repo = QueueRepository(session)
    repo.add(make_queue(status_id=seed_statuses["waiting"], queue_number=1))
    repo.add(make_queue(status_id=seed_statuses["waiting"], queue_number=2))
    repo.add(
        make_queue(
            status_id=seed_statuses["waiting"],
            queue_number=1,
            queue_date=date(2026, 1, 2),
        )
    )
    session.commit()
    assert repo.count_for_date(D) == 2
    assert repo.count_for_date(date(2026, 1, 2)) == 1


def test_list_waiting_ordered_by_created(session, seed_statuses):
    repo = QueueRepository(session)
    repo.add(
        make_queue(
            status_id=seed_statuses["waiting"],
            queue_number=2,
            created_offset_seconds=20,
        )
    )
    repo.add(
        make_queue(
            status_id=seed_statuses["waiting"],
            queue_number=1,
            created_offset_seconds=10,
        )
    )
    session.commit()
    waiting = repo.list_waiting_ordered(D, seed_statuses["waiting"])
    assert [q.queue_number for q in waiting] == [1, 2]


def test_get_next_to_call_prioritizes_checked_in(session, seed_statuses):
    repo = QueueRepository(session)
    # Earlier created but NOT checked in.
    repo.add(
        make_queue(
            status_id=seed_statuses["waiting"],
            queue_number=1,
            created_offset_seconds=10,
        )
    )
    # Later created but checked in -> should be picked first.
    repo.add(
        make_queue(
            status_id=seed_statuses["waiting"],
            queue_number=2,
            created_offset_seconds=20,
            is_checked_in=True,
        )
    )
    session.commit()
    nxt = repo.get_next_to_call(D, seed_statuses["waiting"])
    assert nxt.queue_number == 2


def test_get_next_to_call_none_when_empty(session, seed_statuses):
    repo = QueueRepository(session)
    assert repo.get_next_to_call(D, seed_statuses["waiting"]) is None


def test_position_of(session, seed_statuses):
    repo = QueueRepository(session)
    first = make_queue(
        status_id=seed_statuses["waiting"],
        queue_number=1,
        created_offset_seconds=10,
    )
    second = make_queue(
        status_id=seed_statuses["waiting"],
        queue_number=2,
        created_offset_seconds=20,
    )
    repo.add(first)
    repo.add(second)
    session.commit()
    assert repo.position_of(first, seed_statuses["waiting"]) == 0
    assert repo.position_of(second, seed_statuses["waiting"]) == 1


def test_position_of_zero_when_not_waiting(session, seed_statuses):
    repo = QueueRepository(session)
    served = make_queue(status_id=seed_statuses["served"], queue_number=1)
    repo.add(served)
    session.commit()
    assert repo.position_of(served, seed_statuses["waiting"]) == 0


def test_served_durations_minutes(session, seed_statuses):
    repo = QueueRepository(session)
    q = make_queue(status_id=seed_statuses["served"], queue_number=1)
    q.called_at = utc_naive(0)
    q.served_at = utc_naive(6)  # 6 minutes later
    repo.add(q)
    # A served queue missing timestamps should be ignored.
    q2 = make_queue(status_id=seed_statuses["served"], queue_number=2)
    repo.add(q2)
    session.commit()
    durations = repo.served_durations_minutes(D, seed_statuses["served"])
    assert len(durations) == 1
    assert round(durations[0]) == 6


def test_list_filtered(session, seed_statuses):
    repo = QueueRepository(session)
    repo.add(
        make_queue(
            status_id=seed_statuses["waiting"],
            queue_number=1,
            is_checked_in=True,
        )
    )
    repo.add(
        make_queue(status_id=seed_statuses["called"], queue_number=2)
    )
    session.commit()

    assert len(repo.list_filtered()) == 2
    assert len(repo.list_filtered(queue_date=D)) == 2
    assert len(repo.list_filtered(status_id=seed_statuses["called"])) == 1
    assert len(repo.list_filtered(is_checked_in=True)) == 1
    assert len(repo.list_filtered(limit=1)) == 1
    assert len(repo.list_filtered(offset=2)) == 0


# --------------------------- Status repo --------------------------- #
def test_status_get_by_name_and_in_use(session, seed_statuses):
    repo = QueueStatusRepository(session)
    waiting = repo.get_by_name("waiting")
    assert waiting is not None
    assert repo.get_by_name("ghost") is None

    assert repo.is_in_use(seed_statuses["waiting"]) is False
    QueueRepository(session).add(
        make_queue(status_id=seed_statuses["waiting"], queue_number=1)
    )
    session.commit()
    assert repo.is_in_use(seed_statuses["waiting"]) is True


def test_status_list_all(session, seed_statuses):
    assert len(QueueStatusRepository(session).list_all()) == 6


# --------------------------- Settings repo --------------------------- #
def test_settings_get_active_returns_latest(session):
    repo = QueueSettingsRepository(session)
    assert repo.get_active() is None
    older = make_settings(prefix="OLD")
    repo.add(older)
    session.commit()
    newer = make_settings(prefix="NEW")
    repo.add(newer)
    session.commit()
    assert repo.get_active().prefix == "NEW"


# --------------------------- Log repo --------------------------- #
def test_log_list_by_queue(session, seed_statuses):
    repo = QueueStatusLogRepository(session)
    qid = uuid.uuid4()
    repo.add(
        QueueStatusLog(
            queue_id=qid,
            previous_status=None,
            new_status="waiting",
            trigger_type=TriggerType.SYSTEM,
        )
    )
    repo.add(
        QueueStatusLog(
            queue_id=uuid.uuid4(),
            previous_status="waiting",
            new_status="called",
            trigger_type=TriggerType.ADMIN,
        )
    )
    session.commit()
    logs = repo.list_by_queue(qid)
    assert len(logs) == 1
    assert logs[0].new_status == "waiting"


# --------------------------- Notification repo --------------------------- #
def test_notification_filtered_and_exists(session):
    repo = QueueNotificationRepository(session)
    qid = uuid.uuid4()
    cid = uuid.uuid4()
    repo.add(
        QueueNotification(
            queue_id=qid,
            customer_id=cid,
            notification_type=NotificationType.CONFIRMATION,
            status=NotificationStatus.SENT,
        )
    )
    repo.add(
        QueueNotification(
            queue_id=uuid.uuid4(),
            customer_id=uuid.uuid4(),
            notification_type=NotificationType.CALLED,
            status=NotificationStatus.PENDING,
        )
    )
    session.commit()

    assert len(repo.list_filtered()) == 2
    assert len(repo.list_filtered(queue_id=qid)) == 1
    assert len(repo.list_filtered(customer_id=cid)) == 1
    assert len(repo.list_filtered(status=NotificationStatus.SENT)) == 1
    assert repo.exists_for_queue_type(qid, NotificationType.CONFIRMATION)
    assert not repo.exists_for_queue_type(qid, NotificationType.PREPARE)


def test_base_repo_get_list_and_delete(session, seed_statuses):
    repo = QueueStatusRepository(session)
    status = repo.get_by_name("waiting")
    fetched = repo.get(status.id)
    assert fetched.id == status.id
    # BaseRepository.list with pagination.
    assert len(repo.list(limit=2)) == 2
    custom = repo.get_by_name("served")
    repo.delete(custom)
    session.commit()
    assert repo.get(custom.id) is None


def test_db_base_aggregates_metadata():
    import app.db.base as db_base

    assert "queue" in db_base.metadata.tables
    assert "queue_status" in db_base.metadata.tables
