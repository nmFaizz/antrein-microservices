import uuid
from typing import Optional

from sqlmodel import func, select

from app.models.queue import Queue
from app.models.queue_status import QueueStatus
from app.repositories.base import BaseRepository


class QueueStatusRepository(BaseRepository[QueueStatus]):
    model = QueueStatus

    def list_all(self) -> list[QueueStatus]:
        return list(self.session.exec(select(QueueStatus)).all())

    def get_by_name(self, name: str) -> Optional[QueueStatus]:
        statement = select(QueueStatus).where(QueueStatus.name == name)
        return self.session.exec(statement).first()

    def is_in_use(self, status_id: uuid.UUID) -> bool:
        statement = (
            select(func.count())
            .select_from(Queue)
            .where(Queue.status_id == status_id)
        )
        return self.session.exec(statement).one() > 0
