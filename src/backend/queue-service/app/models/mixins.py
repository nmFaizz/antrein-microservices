from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


def utcnow() -> datetime:
    """Timezone-aware current UTC timestamp (used as a column default)."""
    return datetime.now(timezone.utc)


class TimestampMixin(SQLModel):
    """Adds ``created_at`` / ``updated_at`` columns to a table model.

    Not a table itself; mix into a model declared with ``table=True``.
    """

    created_at: datetime = Field(default_factory=utcnow, nullable=False)
    updated_at: datetime = Field(
        default_factory=utcnow,
        nullable=False,
        sa_column_kwargs={"onupdate": utcnow},
    )
