import uuid

import pytest

from app.lib.exceptions import SettingsNotConfigured, SettingsNotFound
from app.repositories.queue_settings import QueueSettingsRepository
from app.schemas.queue_settings import QueueSettingsCreate, QueueSettingsUpdate
from app.services.queue_settings_service import QueueSettingsService


def _service(session) -> QueueSettingsService:
    return QueueSettingsService(session, QueueSettingsRepository(session))


def test_get_active_raises_when_unconfigured(session):
    with pytest.raises(SettingsNotConfigured):
        _service(session).get_active()


def test_create_and_get_active(session):
    service = _service(session)
    created = service.create(
        QueueSettingsCreate(
            prefix="A",
            grace_period_mins=5,
            avg_serve_time_mins=4,
            max_queue_per_day=50,
            created_by=uuid.uuid4(),
        )
    )
    assert created.id is not None
    assert service.get_active().prefix == "A"


def test_update_partial(session):
    service = _service(session)
    created = service.create(
        QueueSettingsCreate(
            prefix="A",
            grace_period_mins=5,
            avg_serve_time_mins=4,
            max_queue_per_day=50,
            created_by=uuid.uuid4(),
        )
    )
    updated = service.update(
        created.id, QueueSettingsUpdate(is_queue_open=False, prefix="B")
    )
    assert updated.is_queue_open is False
    assert updated.prefix == "B"
    # Untouched field retained.
    assert updated.max_queue_per_day == 50


def test_update_unknown_id_raises(session):
    with pytest.raises(SettingsNotFound):
        _service(session).update(uuid.uuid4(), QueueSettingsUpdate(prefix="Z"))
