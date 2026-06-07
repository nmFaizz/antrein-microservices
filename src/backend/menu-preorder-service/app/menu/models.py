import uuid
from uuid import UUID
from datetime import datetime
from typing import Optional
from enum import Enum
from sqlmodel import SQLModel, Field, Column, DateTime, func

class MenuCategory(str, Enum):
    MAKANAN = "makanan"
    MINUMAN = "minuman"

class MenuBase(SQLModel):
    name: str = Field(max_length=100, schema_extra={"examples": ["Nasi Goreng"]})
    description: Optional[str] = Field(default=None, max_length=255, schema_extra={"examples": ["Nasi goreng pedas dengan telur"]})
    price: float = Field(gt=0, schema_extra={"examples": [15000.0]})
    category: MenuCategory = Field(default=None, schema_extra={"examples": ["makanan"]})

class Menu(MenuBase, table=True):
    __tablename__ = "menu_items"

    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    )
    is_available: bool = Field(default=True)
    is_deleted: bool = Field(default=False)

class MenuCreate(MenuBase):
    pass

class MenuUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[MenuCategory] = None
    is_available: Optional[bool] = None
    is_deleted: Optional[bool] = None
