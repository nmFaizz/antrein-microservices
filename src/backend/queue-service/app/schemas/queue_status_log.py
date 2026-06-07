import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel

from app.models.enums import TriggerType


class QueueStatusLogRead(SQLModel):
    id: uuid.UUID
    queue_id: uuid.UUID
    previous_status: Optional[str]
    new_status: str
    triggered_by: Optional[uuid.UUID]
    trigger_type: TriggerType
    notes: Optional[str]
    created_at: datetime
