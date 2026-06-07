import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.dependencies import NotificationRepoDep
from app.models.enums import NotificationStatus
from app.schemas.common import PaginationParams, pagination_params
from app.schemas.queue_notification import QueueNotificationRead
from app.schemas.response import APIResponse, ok

router = APIRouter(prefix="/queue-notifications", tags=["queue-notifications"])


@router.get("", response_model=APIResponse[list[QueueNotificationRead]])
def list_notifications(
    notification_repo: NotificationRepoDep,
    pagination: PaginationParams = Depends(pagination_params),
    queue_id: Optional[uuid.UUID] = Query(default=None),
    customer_id: Optional[uuid.UUID] = Query(default=None),
    status: Optional[NotificationStatus] = Query(default=None),
):
    notifications = [
        QueueNotificationRead.model_validate(n, from_attributes=True)
        for n in notification_repo.list_filtered(
            queue_id=queue_id,
            customer_id=customer_id,
            status=status,
            offset=pagination.offset,
            limit=pagination.limit,
        )
    ]
    return ok(notifications, "Notifications retrieved")
