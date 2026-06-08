import uuid

import pytest

from app.lib.constants import DefaultStatus
from app.lib.exceptions import StatusNotFound
from app.repositories.queue_status import QueueStatusRepository
from app.services.status_resolver import StatusResolver


def test_id_for_and_name_for(session, seed_statuses):
    resolver = StatusResolver(QueueStatusRepository(session))
    waiting_id = resolver.id_for(DefaultStatus.WAITING)
    assert waiting_id == seed_statuses["waiting"]
    assert resolver.name_for(waiting_id) == "waiting"


def test_id_for_uses_cache(session, seed_statuses, monkeypatch):
    repo = QueueStatusRepository(session)
    resolver = StatusResolver(repo)
    resolver.id_for(DefaultStatus.WAITING)

    # After caching, a second lookup must not hit the repository again.
    def fail(*args, **kwargs):
        raise AssertionError("repository should not be queried on cache hit")

    monkeypatch.setattr(repo, "get_by_name", fail)
    assert resolver.id_for(DefaultStatus.WAITING) == seed_statuses["waiting"]


def test_name_for_uses_cache(session, seed_statuses, monkeypatch):
    repo = QueueStatusRepository(session)
    resolver = StatusResolver(repo)
    waiting_id = seed_statuses["waiting"]
    resolver.name_for(waiting_id)

    monkeypatch.setattr(
        repo, "get", lambda *a, **k: (_ for _ in ()).throw(AssertionError())
    )
    assert resolver.name_for(waiting_id) == "waiting"


def test_id_for_unknown_name_raises(session, seed_statuses):
    resolver = StatusResolver(QueueStatusRepository(session))
    with pytest.raises(StatusNotFound):
        resolver.id_for("nonexistent")


def test_name_for_unknown_id_raises(session, seed_statuses):
    resolver = StatusResolver(QueueStatusRepository(session))
    with pytest.raises(StatusNotFound):
        resolver.name_for(uuid.uuid4())
