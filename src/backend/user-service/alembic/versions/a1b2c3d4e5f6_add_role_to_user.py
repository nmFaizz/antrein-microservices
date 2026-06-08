"""add role to user

Revision ID: a1b2c3d4e5f6
Revises: 06cd01114546
Create Date: 2026-06-09 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '06cd01114546'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

userrole_enum = sa.Enum('admin', 'user', name='userrole')


def upgrade() -> None:
    userrole_enum.create(op.get_bind(), checkfirst=True)
    op.add_column(
        'user',
        sa.Column('role', userrole_enum, nullable=False, server_default='user'),
    )


def downgrade() -> None:
    op.drop_column('user', 'role')
    userrole_enum.drop(op.get_bind(), checkfirst=True)
