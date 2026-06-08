"""add customer_name to preorders

Revision ID: c4d392ef1a03
Revises: a2b170adf789
Create Date: 2026-06-09 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'c4d392ef1a03'
down_revision: Union[str, Sequence[str], None] = 'a2b170adf789'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'preorders',
        sa.Column('customer_name', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('preorders', 'customer_name')
