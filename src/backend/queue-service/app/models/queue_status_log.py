import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel

from app.models.enums import TriggerType
from app.models.mixins import utcnow


class QueueStatusLog(SQLModel, table=True):
    """Immutable audit trail of queue status transitions.

    Status names are stored as snapshots so history stays accurate even if a
    :class:`QueueStatus` row is later renamed or deleted.
    """

    __tablename__ = "queue_status_log"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    queue_id: uuid.UUID = Field(foreign_key="queue.id", index=True)

    previous_status: Optional[str] = Field(default=None)
    new_status: str

    triggered_by: Optional[uuid.UUID] = Field(default=None)
    trigger_type: TriggerType

    notes: Optional[str] = Field(default=None)

    created_at: datetime = Field(default_factory=utcnow, nullable=False)
