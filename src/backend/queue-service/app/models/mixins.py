from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


def utcnow() -> datetime:
    """Naive UTC timestamp (matches the timezone-naive DateTime columns).

    Kept naive so values set in-memory and values reloaded from the database
    can be compared/subtracted without tz-aware/naive mismatches.
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)


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
