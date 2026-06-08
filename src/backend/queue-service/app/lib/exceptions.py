from fastapi import status


class QueueServiceError(Exception):
    """Base class for domain errors mapped to HTTP responses.

    Subclasses set ``status_code``; the message passed at construction time is
    surfaced to the client in the response envelope.
    """

    status_code: int = status.HTTP_400_BAD_REQUEST
    default_message: str = "Queue service error"

    def __init__(self, message: str | None = None) -> None:
        self.message = message or self.default_message
        super().__init__(self.message)


class QueueNotFound(QueueServiceError):
    status_code = status.HTTP_404_NOT_FOUND
    default_message = "Queue not found"


class StatusNotFound(QueueServiceError):
    status_code = status.HTTP_404_NOT_FOUND
    default_message = "Queue status not found"


class SettingsNotFound(QueueServiceError):
    status_code = status.HTTP_404_NOT_FOUND
    default_message = "Queue settings not found"


class SettingsNotConfigured(QueueServiceError):
    status_code = status.HTTP_409_CONFLICT
    default_message = "Queue settings have not been configured"


class StatusInUse(QueueServiceError):
    status_code = status.HTTP_409_CONFLICT
    default_message = "Queue status is in use and cannot be deleted"


class ProtectedStatus(QueueServiceError):
    status_code = status.HTTP_409_CONFLICT
    default_message = "Default queue statuses cannot be renamed or deleted"


class QueueClosed(QueueServiceError):
    status_code = status.HTTP_409_CONFLICT
    default_message = "The queue is currently closed"


class OutsideOperatingHours(QueueServiceError):
    status_code = status.HTTP_409_CONFLICT
    default_message = "Current time is outside the configured operating hours"


class DailyQuotaExceeded(QueueServiceError):
    status_code = status.HTTP_409_CONFLICT
    default_message = "Maximum number of queues for today has been reached"


class InvalidStateTransition(QueueServiceError):
    status_code = status.HTTP_409_CONFLICT
    default_message = "Invalid queue status transition"


class NoQueueToCall(QueueServiceError):
    status_code = status.HTTP_404_NOT_FOUND
    default_message = "There is no waiting queue to call"
