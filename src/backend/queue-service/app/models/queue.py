import uuid
from datetime import date, datetime
from typing import Optional

from sqlmodel import Field

from app.models.mixins import TimestampMixin


class Queue(TimestampMixin, table=True):
    """A customer's ticket in the queue for a given day."""

    __tablename__ = "queue"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    # Cross-service references (no FK: rows live in other services' databases).
    user_id: uuid.UUID = Field(index=True)
    preorder_id: Optional[uuid.UUID] = Field(default=None, index=True)

    queue_number: int = Field(index=True)
    queue_date: date = Field(index=True)
    estimated_time: Optional[datetime] = Field(default=None)

    is_checked_in: bool = Field(default=False)
    checked_in_at: Optional[datetime] = Field(default=None)

    # Same-database relation: real foreign key.
    status_id: uuid.UUID = Field(foreign_key="queue_status.id", index=True)

    called_at: Optional[datetime] = Field(default=None)
    served_at: Optional[datetime] = Field(default=None)
    cancelled_at: Optional[datetime] = Field(default=None)

    # Admin references from user-service (no FK).
    called_by: Optional[uuid.UUID] = Field(default=None)
    served_by: Optional[uuid.UUID] = Field(default=None)
    skipped_by: Optional[uuid.UUID] = Field(default=None)

    is_requeued: bool = Field(default=False)
    # Self-reference to the original ticket when a customer is requeued.
    original_queue_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="queue.id"
    )
