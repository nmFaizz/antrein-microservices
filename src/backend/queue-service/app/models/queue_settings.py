import uuid
from datetime import time
from typing import Optional

from sqlmodel import Field

from app.models.mixins import TimestampMixin


class QueueSettings(TimestampMixin, table=True):
    """Per-tenant queue configuration."""

    __tablename__ = "queue_settings"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    prefix: str
    grace_period_mins: int
    avg_serve_time_mins: int
    max_queue_per_day: int

    is_queue_open: bool = Field(default=True)
    open_time: Optional[time] = Field(default=None)
    close_time: Optional[time] = Field(default=None)

    created_by: uuid.UUID
