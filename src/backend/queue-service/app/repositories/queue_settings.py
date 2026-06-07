from typing import Optional

from sqlmodel import select

from app.models.queue_settings import QueueSettings
from app.repositories.base import BaseRepository


class QueueSettingsRepository(BaseRepository[QueueSettings]):
    model = QueueSettings

    def get_active(self) -> Optional[QueueSettings]:
        """Most recently created settings row (the active configuration)."""
        statement = select(QueueSettings).order_by(
            QueueSettings.created_at.desc()
        )
        return self.session.exec(statement).first()
