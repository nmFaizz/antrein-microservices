import os
from typing import Generator

# Must be set before importing app modules: app.lib.config.Settings() reads it
# at import time. Tests use their own in-memory engine, so the value is a dummy.
os.environ.setdefault("DATABASE_URL", "sqlite://")

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.clients.notification_dispatcher import NotificationDispatcher
from app.clients.preorder_service import PreorderServiceClient
from app.clients.user_service import UserServiceClient
from app.db.session import get_session
from app.lib.constants import DEFAULT_STATUS_COLORS, DefaultStatus
from app.main import app
from app.models.queue_settings import QueueSettings
from app.models.queue_status import QueueStatus
from app.repositories.queue import QueueRepository
from app.repositories.queue_notification import QueueNotificationRepository
from app.repositories.queue_settings import QueueSettingsRepository
from app.repositories.queue_status import QueueStatusRepository
from app.repositories.queue_status_log import QueueStatusLogRepository
from app.services.notification_service import NotificationService
from app.services.queue_service import QueueService
from app.services.status_resolver import StatusResolver
from tests.factories import make_settings


@pytest.fixture(name="engine")
def engine_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="session")
def session_fixture(engine) -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


@pytest.fixture(name="seed_statuses")
def seed_statuses_fixture(session: Session) -> dict[str, object]:
    """Insert the canonical default statuses; return a name -> id map."""
    name_to_id: dict[str, object] = {}
    for status in DefaultStatus:
        row = QueueStatus(name=status.value, color=DEFAULT_STATUS_COLORS[status])
        session.add(row)
        name_to_id[status.value] = row.id
    session.commit()
    return name_to_id


@pytest.fixture(name="settings_row")
def settings_row_fixture(session: Session) -> QueueSettings:
    row = make_settings()
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


@pytest.fixture(name="queue_service")
def queue_service_fixture(
    session: Session, seed_statuses: dict[str, object]
) -> QueueService:
    notification_repo = QueueNotificationRepository(session)
    notification_service = NotificationService(
        notification_repo, UserServiceClient(), NotificationDispatcher()
    )
    # No-op preorder client (base_url=None) so the callback is disabled in tests.
    preorder_client = PreorderServiceClient(
        base_url=None, secret_key=None, service_account_id="test-account"
    )
    return QueueService(
        session=session,
        queue_repo=QueueRepository(session),
        settings_repo=QueueSettingsRepository(session),
        log_repo=QueueStatusLogRepository(session),
        notification_repo=notification_repo,
        resolver=StatusResolver(QueueStatusRepository(session)),
        notification_service=notification_service,
        preorder_client=preorder_client,
    )


@pytest.fixture(name="client")
def client_fixture(session: Session) -> Generator[TestClient, None, None]:
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    # raise_server_exceptions=False so the generic 500 handler is exercised.
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client
    app.dependency_overrides.clear()
