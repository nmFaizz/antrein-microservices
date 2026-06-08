from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from app.auth.dependencies import get_current_user, require_admin
from app.clients.notification_dispatcher import NotificationDispatcher
from app.clients.preorder_service import PreorderServiceClient
from app.clients.user_service import UserServiceClient
from app.db.session import get_session
from app.lib.config import settings
from app.repositories.queue import QueueRepository
from app.repositories.queue_notification import QueueNotificationRepository
from app.repositories.queue_settings import QueueSettingsRepository
from app.repositories.queue_status import QueueStatusRepository
from app.repositories.queue_status_log import QueueStatusLogRepository
from app.services.notification_service import NotificationService
from app.services.queue_service import QueueService
from app.services.queue_settings_service import QueueSettingsService
from app.services.queue_status_service import QueueStatusService
from app.services.status_resolver import StatusResolver

SessionDep = Annotated[Session, Depends(get_session)]
CurrentUserDep = Annotated[dict, Depends(get_current_user)]
AdminDep = Annotated[dict, Depends(require_admin)]


def get_queue_service(session: SessionDep) -> QueueService:
    status_repo = QueueStatusRepository(session)
    notification_repo = QueueNotificationRepository(session)
    notification_service = NotificationService(
        notification_repo, UserServiceClient(), NotificationDispatcher()
    )
    preorder_client = PreorderServiceClient(
        base_url=settings.PREORDER_SERVICE_URL,
        secret_key=settings.SECRET_KEY,
        service_account_id=settings.SERVICE_ACCOUNT_ID,
    )
    return QueueService(
        session=session,
        queue_repo=QueueRepository(session),
        settings_repo=QueueSettingsRepository(session),
        log_repo=QueueStatusLogRepository(session),
        notification_repo=notification_repo,
        resolver=StatusResolver(status_repo),
        notification_service=notification_service,
        preorder_client=preorder_client,
    )


def get_queue_status_service(session: SessionDep) -> QueueStatusService:
    return QueueStatusService(session, QueueStatusRepository(session))


def get_queue_settings_service(session: SessionDep) -> QueueSettingsService:
    return QueueSettingsService(session, QueueSettingsRepository(session))


def get_status_log_repo(session: SessionDep) -> QueueStatusLogRepository:
    return QueueStatusLogRepository(session)


def get_notification_repo(session: SessionDep) -> QueueNotificationRepository:
    return QueueNotificationRepository(session)


QueueServiceDep = Annotated[QueueService, Depends(get_queue_service)]
QueueStatusServiceDep = Annotated[
    QueueStatusService, Depends(get_queue_status_service)
]
QueueSettingsServiceDep = Annotated[
    QueueSettingsService, Depends(get_queue_settings_service)
]
StatusLogRepoDep = Annotated[
    QueueStatusLogRepository, Depends(get_status_log_repo)
]
NotificationRepoDep = Annotated[
    QueueNotificationRepository, Depends(get_notification_repo)
]
