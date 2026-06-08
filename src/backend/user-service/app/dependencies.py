import uuid
from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlmodel import Session

from app.db.session import get_session
from app.lib.exceptions import InvalidCredentials, UsernameNotFound
from app.lib.security import decode_access_token
from app.models.user import User
from app.repositories.user import UserRepository
from app.services.user import UserService

SessionDep = Annotated[Session, Depends(get_session)]

_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_user_service(session: SessionDep) -> UserService:
    return UserService(session, UserRepository(session))


UserServiceDep = Annotated[UserService, Depends(get_user_service)]


def get_current_user(
    token: Annotated[str, Depends(_oauth2_scheme)],
    service: UserServiceDep,
) -> User:
    try:
        user_id = decode_access_token(token)
        return service.get_by_id(uuid.UUID(user_id))
    except (JWTError, ValueError, UsernameNotFound):
        raise InvalidCredentials()


CurrentUserDep = Annotated[User, Depends(get_current_user)]
