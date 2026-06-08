import uuid

import pytest

from app.lib.exceptions import ProtectedStatus, StatusInUse, StatusNotFound
from app.repositories.queue import QueueRepository
from app.repositories.queue_status import QueueStatusRepository
from app.schemas.queue_status import QueueStatusCreate, QueueStatusUpdate
from app.services.queue_status_service import QueueStatusService
from tests.factories import make_queue


def _service(session) -> QueueStatusService:
    return QueueStatusService(session, QueueStatusRepository(session))


def test_list_and_get(session, seed_statuses):
    service = _service(session)
    assert len(service.list()) == 6
    got = service.get(seed_statuses["waiting"])
    assert got.name == "waiting"


def test_get_missing_raises(session, seed_statuses):
    with pytest.raises(StatusNotFound):
        _service(session).get(uuid.uuid4())


def test_create_custom(session, seed_statuses):
    created = _service(session).create(
        QueueStatusCreate(name="vip", color="#FFD700")
    )
    assert created.name == "vip"


def test_create_duplicate_raises(session, seed_statuses):
    with pytest.raises(StatusInUse):
        _service(session).create(QueueStatusCreate(name="waiting"))


def test_rename_default_raises(session, seed_statuses):
    with pytest.raises(ProtectedStatus):
        _service(session).update(
            seed_statuses["waiting"], QueueStatusUpdate(name="renamed")
        )


def test_recolor_default_ok(session, seed_statuses):
    updated = _service(session).update(
        seed_statuses["waiting"], QueueStatusUpdate(color="#000000")
    )
    assert updated.color == "#000000"
    assert updated.name == "waiting"


def test_update_missing_raises(session, seed_statuses):
    with pytest.raises(StatusNotFound):
        _service(session).update(uuid.uuid4(), QueueStatusUpdate(color="#fff"))


def test_delete_default_raises(session, seed_statuses):
    with pytest.raises(ProtectedStatus):
        _service(session).delete(seed_statuses["waiting"])


def test_delete_in_use_raises(session, seed_statuses):
    service = _service(session)
    custom = service.create(QueueStatusCreate(name="vip"))
    QueueRepository(session).add(
        make_queue(status_id=custom.id, queue_number=1)
    )
    session.commit()
    with pytest.raises(StatusInUse):
        service.delete(custom.id)


def test_delete_unused_custom_ok(session, seed_statuses):
    service = _service(session)
    custom = service.create(QueueStatusCreate(name="vip"))
    service.delete(custom.id)
    with pytest.raises(StatusNotFound):
        service.get(custom.id)
