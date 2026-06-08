from typing import Optional

from sqlmodel import select

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User

    def add_user(self, username: str, password: str) -> User:
        user = User(
            username=username,
            password=password,
        )

        self.session.add(user)

        return user

    def find_by_username(
        self,
        username: str,
    ) -> Optional[User]:
        statement = select(User).where(
            User.username == username
        )

        return self.session.exec(statement).first()