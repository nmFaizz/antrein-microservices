import uuid

from sqlmodel import Session

from app.lib.exceptions import SettingsNotConfigured, SettingsNotFound
from app.models.queue_settings import QueueSettings
from app.repositories.queue_settings import QueueSettingsRepository
from app.schemas.queue_settings import QueueSettingsCreate, QueueSettingsUpdate


class QueueSettingsService:
    """CRUD for the queue configuration."""

    def __init__(
        self, session: Session, settings_repo: QueueSettingsRepository
    ) -> None:
        self.session = session
        self.settings_repo = settings_repo

    def get_active(self) -> QueueSettings:
        settings = self.settings_repo.get_active()
        if settings is None:
            raise SettingsNotConfigured()
        return settings

    def create(self, data: QueueSettingsCreate) -> QueueSettings:
        settings = QueueSettings.model_validate(data)
        self.settings_repo.add(settings)
        self.session.commit()
        self.session.refresh(settings)
        return settings

    def update(
        self, settings_id: uuid.UUID, data: QueueSettingsUpdate
    ) -> QueueSettings:
        settings = self.settings_repo.get(settings_id)
        if settings is None:
            raise SettingsNotFound()
        settings.sqlmodel_update(data.model_dump(exclude_unset=True))
        self.settings_repo.add(settings)
        self.session.commit()
        self.session.refresh(settings)
        return settings
