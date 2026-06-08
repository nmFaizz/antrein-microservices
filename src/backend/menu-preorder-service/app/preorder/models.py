import uuid
from uuid import UUID
from datetime import datetime
from typing import Optional, List
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship, Column, DateTime, func
from sqlalchemy import JSON
from app.menu.models import Menu

class PreorderItemBase(SQLModel):
    menu_item_id: UUID = Field(foreign_key="menu_items.id", schema_extra={"examples": [str(uuid.uuid4())]})
    quantity: int = Field(gt=0, schema_extra={"examples": [1]})

class PreorderItem(PreorderItemBase, table=True):
    __tablename__ = "preorder_items"

    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    preorder_id: UUID = Field(foreign_key="preorders.id")
    subtotal: float = Field(gt=0, schema_extra={"examples": [30000.0]})

    preorder: "Preorder" = Relationship(back_populates="items")
    menu: Menu = Relationship()


class PreorderBase(SQLModel):
    notes: Optional[str] = Field(default=None, max_length=255, schema_extra={"examples": ["Pedas, tanpa sayur"]})

class PreorderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"

class Preorder(PreorderBase, table=True):
    __tablename__ = "preorders"

    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    user_id: UUID = Field(schema_extra={"examples": [str(uuid.uuid4())]})
    customer_name: Optional[str] = Field(default=None, max_length=100)
    total_price: float = Field(schema_extra={"examples": [30000.0]})
    status: PreorderStatus = Field(default=PreorderStatus.PENDING, schema_extra={"examples": [PreorderStatus.PENDING]})
    queue: Optional[dict] = Field(default=None, sa_column=Column(JSON, nullable=True))
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    )

    items: List[PreorderItem] = Relationship(back_populates="preorder")

class PreorderItemCreate(PreorderItemBase):
    pass

class PreorderCreate(PreorderBase):
    items: List[PreorderItemCreate] = Field(schema_extra={"examples": [[{"menu_item_id": str(uuid.uuid4()), "quantity": 1}]]})

class PreorderUpdate(SQLModel):
    status: Optional[PreorderStatus] = Field(default=None, description="New status of the preorder")
    queue: Optional[dict] = Field(default=None, description="Queue details from the queue service")

class PreorderItemResponse(SQLModel):
    menu_item_id: UUID
    quantity: int
    subtotal: float
    menu: Optional[Menu] = None

class PreorderResponse(PreorderBase):
    id: UUID
    user_id: UUID
    customer_name: Optional[str] = None
    total_price: float
    status: PreorderStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: List[PreorderItemResponse] = []
    queue: Optional[dict] = None
