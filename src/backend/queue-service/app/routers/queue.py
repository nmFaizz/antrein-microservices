import uuid
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query, status

from app.dependencies import (
    AdminDep,
    CurrentUserDep,
    NotificationRepoDep,
    QueueServiceDep,
    StatusLogRepoDep,
)
from app.schemas.common import PaginationParams, pagination_params
from app.schemas.queue import (
    CallNextRequest,
    CancelRequest,
    CheckInRequest,
    QueueCreate,
    QueueRead,
    RequeueRequest,
    ServeRequest,
    SkipRequest,
)
from app.schemas.queue_notification import QueueNotificationRead
from app.schemas.queue_status_log import QueueStatusLogRead
from app.schemas.response import APIResponse, ok

router = APIRouter(prefix="/queues", tags=["queues"])


@router.post(
    "",
    response_model=APIResponse[QueueRead],
    status_code=status.HTTP_201_CREATED,
)
def create_queue(payload: QueueCreate, _: AdminDep, service: QueueServiceDep):
    queue = service.create_queue(payload)
    return ok(queue, "Queue created")


@router.get("", response_model=APIResponse[list[QueueRead]])
def list_queues(
    _: AdminDep,
    service: QueueServiceDep,
    pagination: PaginationParams = Depends(pagination_params),
    queue_date: Optional[date] = Query(default=None),
    status_id: Optional[uuid.UUID] = Query(default=None),
    is_checked_in: Optional[bool] = Query(default=None),
):
    queues = service.list(
        queue_date=queue_date,
        status_id=status_id,
        is_checked_in=is_checked_in,
        offset=pagination.offset,
        limit=pagination.limit,
    )
    return ok(queues, "Queues retrieved")


@router.post("/call-next", response_model=APIResponse[QueueRead])
def call_next(payload: CallNextRequest, current_user: AdminDep, service: QueueServiceDep):
    admin_id = uuid.UUID(current_user["user_id"])
    queue = service.call_next(payload, admin_id)
    return ok(queue, "Next queue called")


@router.get("/{queue_id}", response_model=APIResponse[QueueRead])
def get_queue(queue_id: uuid.UUID, _: CurrentUserDep, service: QueueServiceDep):
    return ok(service.get(queue_id), "Queue retrieved")


@router.post("/{queue_id}/check-in", response_model=APIResponse[QueueRead])
def check_in(
    queue_id: uuid.UUID, payload: CheckInRequest, _: CurrentUserDep, service: QueueServiceDep
):
    return ok(service.check_in(queue_id), "Checked in")


@router.post("/{queue_id}/serve", response_model=APIResponse[QueueRead])
def serve(
    queue_id: uuid.UUID, payload: ServeRequest, current_user: AdminDep, service: QueueServiceDep
):
    admin_id = uuid.UUID(current_user["user_id"])
    return ok(service.serve(queue_id, payload, admin_id), "Queue served")


@router.post("/{queue_id}/skip", response_model=APIResponse[QueueRead])
def skip(queue_id: uuid.UUID, payload: SkipRequest, current_user: AdminDep, service: QueueServiceDep):
    admin_id = uuid.UUID(current_user["user_id"])
    return ok(service.skip(queue_id, payload, admin_id), "Queue skipped")


@router.post("/{queue_id}/requeue", response_model=APIResponse[QueueRead])
def requeue(
    queue_id: uuid.UUID, payload: RequeueRequest, current_user: AdminDep, service: QueueServiceDep
):
    admin_id = uuid.UUID(current_user["user_id"])
    return ok(service.requeue(queue_id, payload, admin_id), "Queue re-queued")


@router.post("/{queue_id}/cancel", response_model=APIResponse[QueueRead])
def cancel(
    queue_id: uuid.UUID, payload: CancelRequest, current_user: CurrentUserDep, service: QueueServiceDep
):
    customer_id = uuid.UUID(current_user["user_id"])
    return ok(service.cancel(queue_id, payload, customer_id), "Queue cancelled")


@router.get(
    "/{queue_id}/logs",
    response_model=APIResponse[list[QueueStatusLogRead]],
)
def get_queue_logs(queue_id: uuid.UUID, _: AdminDep, log_repo: StatusLogRepoDep):
    logs = [
        QueueStatusLogRead.model_validate(log, from_attributes=True)
        for log in log_repo.list_by_queue(queue_id)
    ]
    return ok(logs, "Status logs retrieved")


@router.get(
    "/{queue_id}/notifications",
    response_model=APIResponse[list[QueueNotificationRead]],
)
def get_queue_notifications(
    queue_id: uuid.UUID, _: CurrentUserDep, notification_repo: NotificationRepoDep
):
    notifications = [
        QueueNotificationRead.model_validate(n, from_attributes=True)
        for n in notification_repo.list_filtered(queue_id=queue_id)
    ]
    return ok(notifications, "Notifications retrieved")
