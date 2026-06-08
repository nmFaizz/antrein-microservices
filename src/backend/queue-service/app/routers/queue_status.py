import uuid

from fastapi import APIRouter, status

from app.dependencies import AdminDep, QueueStatusServiceDep
from app.schemas.queue_status import (
    QueueStatusCreate,
    QueueStatusRead,
    QueueStatusUpdate,
)
from app.schemas.response import APIResponse, ok

router = APIRouter(prefix="/queue-statuses", tags=["queue-statuses"])


def _read(status_obj) -> QueueStatusRead:
    return QueueStatusRead.model_validate(status_obj, from_attributes=True)


@router.get("", response_model=APIResponse[list[QueueStatusRead]])
def list_statuses(service: QueueStatusServiceDep):
    statuses = [_read(s) for s in service.list()]
    return ok(statuses, "Queue statuses retrieved")


@router.post(
    "",
    response_model=APIResponse[QueueStatusRead],
    status_code=status.HTTP_201_CREATED,
)
def create_status(payload: QueueStatusCreate, _: AdminDep, service: QueueStatusServiceDep):
    return ok(_read(service.create(payload)), "Queue status created")


@router.get("/{status_id}", response_model=APIResponse[QueueStatusRead])
def get_status(status_id: uuid.UUID, service: QueueStatusServiceDep):
    return ok(_read(service.get(status_id)), "Queue status retrieved")


@router.patch("/{status_id}", response_model=APIResponse[QueueStatusRead])
def update_status(
    status_id: uuid.UUID,
    payload: QueueStatusUpdate,
    _: AdminDep,
    service: QueueStatusServiceDep,
):
    return ok(_read(service.update(status_id, payload)), "Queue status updated")


@router.delete("/{status_id}", response_model=APIResponse[None])
def delete_status(status_id: uuid.UUID, _: AdminDep, service: QueueStatusServiceDep):
    service.delete(status_id)
    return ok(None, "Queue status deleted")
