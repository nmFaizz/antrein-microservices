"""Service tests with mocked repository/session collaborators."""

import uuid
from unittest.mock import Mock

import pytest

from app.lib.exceptions import (
    UsernameNotFound,
    UsernamePasswordIncorrect,
    UsernameTaken,
)
from app.lib.security import hash_password
from app.models.user import User
from app.schemas.user import UserLogin, UserRegister
from app.services.user import UserService


@pytest.fixture()
def user_repo():
    return Mock()


@pytest.fixture()
def db_session():
    return Mock()


@pytest.fixture()
def service(db_session, user_repo):
    return UserService(db_session, user_repo)


def test_register_creates_user_when_username_is_free(service, db_session, user_repo):
    user_repo.find_by_username.return_value = None
    created = User(id=uuid.uuid4(), username="alice", password="hashed")
    user_repo.add_user.return_value = created

    result = service.register(UserRegister(username="alice", password="secret"))

    user_repo.find_by_username.assert_called_once_with("alice")
    username, hashed = user_repo.add_user.call_args.args
    assert username == "alice"
    assert hashed != "secret"
    db_session.commit.assert_called_once()
    db_session.refresh.assert_called_once_with(created)
    assert result is created


def test_register_raises_when_username_taken(service, user_repo):
    user_repo.find_by_username.return_value = User(
        id=uuid.uuid4(), username="alice", password="hashed"
    )

    with pytest.raises(UsernameTaken):
        service.register(UserRegister(username="alice", password="secret"))

    user_repo.add_user.assert_not_called()


def test_authenticate_returns_user_on_correct_password(service, user_repo):
    user = User(id=uuid.uuid4(), username="alice", password=hash_password("secret"))
    user_repo.find_by_username.return_value = user

    result = service.authenticate(UserLogin(username="alice", password="secret"))

    assert result is user


def test_authenticate_raises_when_username_not_found(service, user_repo):
    user_repo.find_by_username.return_value = None

    with pytest.raises(UsernameNotFound):
        service.authenticate(UserLogin(username="ghost", password="secret"))


def test_authenticate_raises_when_password_incorrect(service, user_repo):
    user = User(id=uuid.uuid4(), username="alice", password=hash_password("secret"))
    user_repo.find_by_username.return_value = user

    with pytest.raises(UsernamePasswordIncorrect):
        service.authenticate(UserLogin(username="alice", password="wrong"))


def test_get_by_id_returns_user_when_found(service, user_repo):
    user = User(id=uuid.uuid4(), username="alice", password="hashed")
    user_repo.get.return_value = user

    result = service.get_by_id(user.id)

    user_repo.get.assert_called_once_with(user.id)
    assert result is user


def test_get_by_id_raises_when_not_found(service, user_repo):
    user_repo.get.return_value = None

    with pytest.raises(UsernameNotFound):
        service.get_by_id(uuid.uuid4())
