import uuid
import enum

from sqlalchemy import Column, Enum as SAEnum
from sqlmodel import Field, SQLModel


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"


class User(SQLModel, table=True):
    """A customer model."""

    __tablename__ = "user"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    username: str = Field(index=True)
    password: str
    role: UserRole = Field(
        default=UserRole.USER,
        sa_column=Column(
            SAEnum(UserRole, values_callable=lambda obj: [e.value for e in obj]),
            nullable=False,
            server_default=UserRole.USER.value,
        ),
    )
