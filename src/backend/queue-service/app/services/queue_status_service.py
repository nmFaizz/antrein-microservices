import uuid

from sqlmodel import Session

from app.lib.constants import DefaultStatus
from app.lib.exceptions import (
    ProtectedStatus,
    StatusInUse,
    StatusNotFound,
)
from app.models.queue_status import QueueStatus
from app.repositories.queue_status import QueueStatusRepository
from app.schemas.queue_status import QueueStatusCreate, QueueStatusUpdate

_DEFAULT_NAMES = {status.value for status in DefaultStatus}


class QueueStatusService:
    """CRUD for customizable queue statuses, protecting canonical defaults."""

    def __init__(
        self, session: Session, status_repo: QueueStatusRepository
    ) -> None:
        self.session = session
        self.status_repo = status_repo

    def list(self) -> list[QueueStatus]:
        return self.status_repo.list_all()

    def get(self, status_id: uuid.UUID) -> QueueStatus:
        status = self.status_repo.get(status_id)
        if status is None:
            raise StatusNotFound()
        return status

    def create(self, data: QueueStatusCreate) -> QueueStatus:
        if self.status_repo.get_by_name(data.name) is not None:
            raise StatusInUse(f"Status '{data.name}' already exists")
        status = QueueStatus.model_validate(data)
        self.status_repo.add(status)
        self.session.commit()
        self.session.refresh(status)
        return status

    def update(
        self, status_id: uuid.UUID, data: QueueStatusUpdate
    ) -> QueueStatus:
        status = self.get(status_id)
        changes = data.model_dump(exclude_unset=True)
        new_name = changes.get("name")
        if (
            new_name is not None
            and new_name != status.name
            and status.name in _DEFAULT_NAMES
        ):
            raise ProtectedStatus(
                "Default queue statuses cannot be renamed (color is editable)"
            )
        status.sqlmodel_update(changes)
        self.status_repo.add(status)
        self.session.commit()
        self.session.refresh(status)
        return status

    def delete(self, status_id: uuid.UUID) -> None:
        status = self.get(status_id)
        if status.name in _DEFAULT_NAMES:
            raise ProtectedStatus()
        if self.status_repo.is_in_use(status_id):
            raise StatusInUse()
        self.status_repo.delete(status)
        self.session.commit()
