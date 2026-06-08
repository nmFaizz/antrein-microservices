import uuid

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    """A customer model."""

    __tablename__ = "user"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    username: str = Field(index=True)
    password: str