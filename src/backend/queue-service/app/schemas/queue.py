import uuid
from datetime import date, datetime
from typing import Optional

from sqlmodel import SQLModel

from app.models.enums import TriggerType


class QueueCreate(SQLModel):
    """Inbound payload from the PreOrder Service to enqueue a customer."""

    customer_id: uuid.UUID
    preorder_id: Optional[uuid.UUID] = None
    queue_date: Optional[date] = None


class CheckInRequest(SQLModel):
    """Customer check-in (identity taken from the path queue)."""


class CallNextRequest(SQLModel):
    queue_date: Optional[date] = None


class ServeRequest(SQLModel):
    pass


class SkipRequest(SQLModel):
    trigger_type: TriggerType = TriggerType.ADMIN
    notes: Optional[str] = None


class RequeueRequest(SQLModel):
    pass


class CancelRequest(SQLModel):
    pass


class QueueRead(SQLModel):
    """Queue representation returned to clients, with computed fields."""

    id: uuid.UUID
    user_id: uuid.UUID
    preorder_id: Optional[uuid.UUID]

    queue_number: int
    queue_date: date
    estimated_time: Optional[datetime]

    is_checked_in: bool
    checked_in_at: Optional[datetime]

    status_id: uuid.UUID
    status_name: str

    called_at: Optional[datetime]
    served_at: Optional[datetime]
    cancelled_at: Optional[datetime]

    called_by: Optional[uuid.UUID]
    served_by: Optional[uuid.UUID]
    skipped_by: Optional[uuid.UUID]

    is_requeued: bool
    original_queue_id: Optional[uuid.UUID]

    created_at: datetime
    updated_at: datetime

    # Computed (not stored), see business doc section 6.
    current_position: int
    estimated_wait_minutes: int
