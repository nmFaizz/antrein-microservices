"""seed default queue statuses

Revision ID: b2f4c6d8e0a1
Revises: 8af2a9eb7554
Create Date: 2026-06-07 17:05:00.000000

"""
import uuid
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'b2f4c6d8e0a1'
down_revision: Union[str, Sequence[str], None] = '8af2a9eb7554'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Default statuses, customizable by admins after seeding.
DEFAULT_STATUSES: list[tuple[str, str]] = [
    ("waiting", "#9CA3AF"),
    ("called", "#3B82F6"),
    ("serving", "#F59E0B"),
    ("served", "#10B981"),
    ("skipped", "#F97316"),
    ("cancelled", "#EF4444"),
    ("requeued", "#8B5CF6"),
]


def upgrade() -> None:
    """Insert default queue statuses."""
    queue_status = sa.table(
        "queue_status",
        sa.column("id", sa.Uuid()),
        sa.column("name", sqlmodel.sql.sqltypes.AutoString()),
        sa.column("color", sqlmodel.sql.sqltypes.AutoString()),
    )
    op.bulk_insert(
        queue_status,
        [
            {"id": uuid.uuid4(), "name": name, "color": color}
            for name, color in DEFAULT_STATUSES
        ],
    )


def downgrade() -> None:
    """Remove the seeded default queue statuses."""
    queue_status = sa.table(
        "queue_status",
        sa.column("name", sqlmodel.sql.sqltypes.AutoString()),
    )
    names = [name for name, _ in DEFAULT_STATUSES]
    op.execute(
        queue_status.delete().where(queue_status.c.name.in_(names))
    )
