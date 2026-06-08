import uuid

from sqlmodel import SQLModel


class UserRegister(SQLModel):
    username: str
    password: str


class UserLogin(UserRegister):
    pass


class UserRead(SQLModel):
    id: uuid.UUID
    username: str


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"
