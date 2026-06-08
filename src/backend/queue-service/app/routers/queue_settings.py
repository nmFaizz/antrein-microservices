import uuid

from fastapi import APIRouter, status

from app.dependencies import AdminDep, QueueSettingsServiceDep
from app.schemas.queue_settings import (
    QueueSettingsCreate,
    QueueSettingsRead,
    QueueSettingsUpdate,
)
from app.schemas.response import APIResponse, ok

router = APIRouter(prefix="/queue-settings", tags=["queue-settings"])


def _read(settings) -> QueueSettingsRead:
    return QueueSettingsRead.model_validate(settings, from_attributes=True)


@router.get("", response_model=APIResponse[QueueSettingsRead])
def get_settings(_: AdminDep, service: QueueSettingsServiceDep):
    return ok(_read(service.get_active()), "Queue settings retrieved")


@router.post(
    "",
    response_model=APIResponse[QueueSettingsRead],
    status_code=status.HTTP_201_CREATED,
)
def create_settings(
    payload: QueueSettingsCreate, _: AdminDep, service: QueueSettingsServiceDep
):
    return ok(_read(service.create(payload)), "Queue settings created")


@router.patch("/{settings_id}", response_model=APIResponse[QueueSettingsRead])
def update_settings(
    settings_id: uuid.UUID,
    payload: QueueSettingsUpdate,
    _: AdminDep,
    service: QueueSettingsServiceDep,
):
    return ok(
        _read(service.update(settings_id, payload)), "Queue settings updated"
    )
