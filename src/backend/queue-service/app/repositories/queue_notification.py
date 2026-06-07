import uuid
from typing import Optional

from sqlmodel import func, select

from app.models.enums import NotificationStatus, NotificationType
from app.models.queue_notification import QueueNotification
from app.repositories.base import BaseRepository


class QueueNotificationRepository(BaseRepository[QueueNotification]):
    model = QueueNotification

    def list_filtered(
        self,
        *,
        queue_id: Optional[uuid.UUID] = None,
        customer_id: Optional[uuid.UUID] = None,
        status: Optional[NotificationStatus] = None,
        offset: int = 0,
        limit: int = 50,
    ) -> list[QueueNotification]:
        statement = select(QueueNotification)
        if queue_id is not None:
            statement = statement.where(QueueNotification.queue_id == queue_id)
        if customer_id is not None:
            statement = statement.where(
                QueueNotification.customer_id == customer_id
            )
        if status is not None:
            statement = statement.where(QueueNotification.status == status)
        statement = (
            statement.order_by(QueueNotification.created_at)
            .offset(offset)
            .limit(limit)
        )
        return list(self.session.exec(statement).all())

    def exists_for_queue_type(
        self, queue_id: uuid.UUID, notification_type: NotificationType
    ) -> bool:
        statement = (
            select(func.count())
            .select_from(QueueNotification)
            .where(QueueNotification.queue_id == queue_id)
            .where(QueueNotification.notification_type == notification_type)
        )
        return self.session.exec(statement).one() > 0
