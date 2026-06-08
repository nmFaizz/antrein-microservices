import uuid

from sqlmodel import Session

from app.lib.exceptions import (
    UsernameNotFound,
    UsernamePasswordIncorrect,
    UsernameTaken,
)
from app.lib.security import hash_password, verify_password
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserLogin, UserRegister


class UserService:
    """Registration, authentication, and lookup for user accounts."""

    def __init__(self, session: Session, user_repo: UserRepository) -> None:
        self.session = session
        self.user_repo = user_repo

    def register(self, data: UserRegister) -> User:
        if self.user_repo.find_by_username(data.username) is not None:
            raise UsernameTaken()

        user = self.user_repo.add_user(data.username, hash_password(data.password))
        self.session.commit()
        self.session.refresh(user)
        return user

    def authenticate(self, data: UserLogin) -> User:
        user = self.user_repo.find_by_username(data.username)
        if user is None:
            raise UsernameNotFound()
        if not verify_password(data.password, user.password):
            raise UsernamePasswordIncorrect()

        return user

    def get_by_id(self, user_id: uuid.UUID) -> User:
        user = self.user_repo.get(user_id)
        if user is None:
            raise UsernameNotFound()

        return user
