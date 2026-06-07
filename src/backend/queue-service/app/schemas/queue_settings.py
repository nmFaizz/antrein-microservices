import uuid
from datetime import datetime, time
from typing import Optional

from sqlmodel import SQLModel


class QueueSettingsCreate(SQLModel):
    prefix: str
    grace_period_mins: int
    avg_serve_time_mins: int
    max_queue_per_day: int
    created_by: uuid.UUID

    is_queue_open: bool = True
    open_time: Optional[time] = None
    close_time: Optional[time] = None


class QueueSettingsUpdate(SQLModel):
    prefix: Optional[str] = None
    grace_period_mins: Optional[int] = None
    avg_serve_time_mins: Optional[int] = None
    max_queue_per_day: Optional[int] = None
    is_queue_open: Optional[bool] = None
    open_time: Optional[time] = None
    close_time: Optional[time] = None


class QueueSettingsRead(SQLModel):
    id: uuid.UUID
    prefix: str
    grace_period_mins: int
    avg_serve_time_mins: int
    max_queue_per_day: int
    is_queue_open: bool
    open_time: Optional[time]
    close_time: Optional[time]
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime
