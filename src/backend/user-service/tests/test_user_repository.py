"""Repository tests against a stub (in-memory SQLite) database session."""

from app.repositories.user import UserRepository


def test_add_user_persists_to_session(session):
    repo = UserRepository(session)

    user = repo.add_user("alice", "hashed-password")
    session.commit()

    assert user.id is not None
    assert session.get(type(user), user.id).username == "alice"


def test_find_by_username_returns_match(session):
    repo = UserRepository(session)
    repo.add_user("bob", "hashed-password")
    session.commit()

    found = repo.find_by_username("bob")

    assert found is not None
    assert found.username == "bob"


def test_find_by_username_returns_none_when_missing(session):
    repo = UserRepository(session)

    assert repo.find_by_username("ghost") is None
