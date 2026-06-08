from enum import StrEnum


class DefaultStatus(StrEnum):
    """Canonical queue statuses the business logic depends on.

    These are seeded by the initial data migration and are protected from
    deletion/rename by the status service. Admins may still add their own
    custom statuses and recolor these.
    """

    WAITING = "waiting"
    CALLED = "called"
    SERVED = "served"
    SKIPPED = "skipped"
    RE_QUEUED = "re_queued"
    CANCELLED = "cancelled"


# Default display colors used when seeding the canonical statuses.
DEFAULT_STATUS_COLORS: dict[str, str] = {
    DefaultStatus.WAITING: "#9CA3AF",
    DefaultStatus.CALLED: "#3B82F6",
    DefaultStatus.SERVED: "#10B981",
    DefaultStatus.SKIPPED: "#F97316",
    DefaultStatus.RE_QUEUED: "#8B5CF6",
    DefaultStatus.CANCELLED: "#EF4444",
}

# Allowed status transitions (keyed by canonical status name). Used by the
# queue service to reject illegal moves.
ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    DefaultStatus.WAITING: {
        DefaultStatus.CALLED,
        DefaultStatus.SKIPPED,
        DefaultStatus.CANCELLED,
    },
    DefaultStatus.CALLED: {
        DefaultStatus.SERVED,
        DefaultStatus.SKIPPED,
    },
    DefaultStatus.SERVED: set(),
    DefaultStatus.SKIPPED: {DefaultStatus.RE_QUEUED},
    DefaultStatus.RE_QUEUED: set(),
    DefaultStatus.CANCELLED: set(),
}

# Position thresholds (counting waiting tickets ahead) that trigger a
# customer "get ready" notification.
NOTIFY_PREPARE_POSITION = 3
NOTIFY_ALMOST_POSITION = 1
