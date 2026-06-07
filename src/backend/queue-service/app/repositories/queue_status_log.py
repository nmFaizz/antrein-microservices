import uuid

from sqlmodel import select

from app.models.queue_status_log import QueueStatusLog
from app.repositories.base import BaseRepository


class QueueStatusLogRepository(BaseRepository[QueueStatusLog]):
    model = QueueStatusLog

    def list_by_queue(self, queue_id: uuid.UUID) -> list[QueueStatusLog]:
        statement = (
            select(QueueStatusLog)
            .where(QueueStatusLog.queue_id == queue_id)
            .order_by(QueueStatusLog.created_at)
        )
        return list(self.session.exec(statement).all())
