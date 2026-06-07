import uuid
from typing import Optional

from sqlmodel import Field, SQLModel


class QueueStatus(SQLModel, table=True):
    """Customizable queue status (seeded with defaults, editable by admins)."""

    __tablename__ = "queue_status"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(index=True, unique=True)
    color: Optional[str] = Field(default=None)
