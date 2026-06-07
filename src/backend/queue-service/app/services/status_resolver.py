import uuid

from app.lib.exceptions import StatusNotFound
from app.repositories.queue_status import QueueStatusRepository


class StatusResolver:
    """Resolves between canonical status names and their row ids.

    Caches lookups for the lifetime of the request-scoped instance to avoid
    repeated queries when reading many queues.
    """

    def __init__(self, status_repo: QueueStatusRepository) -> None:
        self.status_repo = status_repo
        self._id_by_name: dict[str, uuid.UUID] = {}
        self._name_by_id: dict[uuid.UUID, str] = {}

    def id_for(self, name: str) -> uuid.UUID:
        if name in self._id_by_name:
            return self._id_by_name[name]
        status = self.status_repo.get_by_name(name)
        if status is None:
            raise StatusNotFound(f"Queue status '{name}' is not configured")
        self._id_by_name[name] = status.id
        self._name_by_id[status.id] = status.name
        return status.id

    def name_for(self, status_id: uuid.UUID) -> str:
        if status_id in self._name_by_id:
            return self._name_by_id[status_id]
        status = self.status_repo.get(status_id)
        if status is None:
            raise StatusNotFound()
        self._name_by_id[status_id] = status.name
        self._id_by_name[status.name] = status.id
        return status.name
