import uuid
import enum
from sqlmodel import Field, SQLModel

class UserRole(str, enum.Enum):
    ADMIN = 'admin'
    USER = 'user'

class User(SQLModel, table=True):
    """A customer model."""

    __tablename__ = "user"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    username: str = Field(index=True)
    password: str
    role: UserRole = Field(default='user')