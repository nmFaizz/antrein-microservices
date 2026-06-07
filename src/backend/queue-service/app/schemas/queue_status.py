import uuid
from typing import Optional

from sqlmodel import SQLModel


class QueueStatusCreate(SQLModel):
    name: str
    color: Optional[str] = None


class QueueStatusUpdate(SQLModel):
    name: Optional[str] = None
    color: Optional[str] = None


class QueueStatusRead(SQLModel):
    id: uuid.UUID
    name: str
    color: Optional[str]
