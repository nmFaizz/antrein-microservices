import uuid
from datetime import date, datetime, time, timedelta, timezone

from app.models.queue import Queue
from app.models.queue_settings import QueueSettings

# Fixed reference instant so created_at ordering is deterministic across tests.
_BASE = datetime(2026, 1, 1, 9, 0, 0)


def make_settings(
    *,
    prefix: str = "A",
    grace_period_mins: int = 5,
    avg_serve_time_mins: int = 4,
    max_queue_per_day: int = 100,
    is_queue_open: bool = True,
    open_time: time | None = time(0, 0, 0),
    close_time: time | None = time(23, 59, 59),
    created_by: uuid.UUID | None = None,
) -> QueueSettings:
    return QueueSettings(
        prefix=prefix,
        grace_period_mins=grace_period_mins,
        avg_serve_time_mins=avg_serve_time_mins,
        max_queue_per_day=max_queue_per_day,
        is_queue_open=is_queue_open,
        open_time=open_time,
        close_time=close_time,
        created_by=created_by or uuid.uuid4(),
    )


def make_queue(
    *,
    status_id: uuid.UUID,
    queue_number: int = 1,
    queue_date: date | None = None,
    created_offset_seconds: int = 0,
    user_id: uuid.UUID | None = None,
    is_checked_in: bool = False,
    **overrides,
) -> Queue:
    """Build a Queue with an explicit increasing created_at for deterministic
    ordering. Pass ``created_offset_seconds`` to control position."""
    created = _BASE + timedelta(seconds=created_offset_seconds)
    queue = Queue(
        user_id=user_id or uuid.uuid4(),
        queue_number=queue_number,
        queue_date=queue_date or date(2026, 1, 1),
        status_id=status_id,
        is_checked_in=is_checked_in,
        created_at=created,
        updated_at=created,
        **overrides,
    )
    return queue


def utc_naive(dt_offset_minutes: int = 0) -> datetime:
    return (
        datetime.now(timezone.utc).replace(tzinfo=None)
        + timedelta(minutes=dt_offset_minutes)
    )
