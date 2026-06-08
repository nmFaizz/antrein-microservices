from app.lib.constants import (
    ALLOWED_TRANSITIONS,
    DEFAULT_STATUS_COLORS,
    NOTIFY_ALMOST_POSITION,
    NOTIFY_PREPARE_POSITION,
    DefaultStatus,
)
from app.lib.exceptions import (
    DailyQuotaExceeded,
    InvalidStateTransition,
    NoQueueToCall,
    OutsideOperatingHours,
    ProtectedStatus,
    QueueClosed,
    QueueNotFound,
    QueueServiceError,
    SettingsNotConfigured,
    SettingsNotFound,
    StatusInUse,
    StatusNotFound,
)


def test_default_statuses_have_colors():
    for status in DefaultStatus:
        assert status in DEFAULT_STATUS_COLORS
        assert DEFAULT_STATUS_COLORS[status].startswith("#")


def test_allowed_transitions_shape():
    assert ALLOWED_TRANSITIONS[DefaultStatus.WAITING] == {
        DefaultStatus.CALLED,
        DefaultStatus.SKIPPED,
        DefaultStatus.CANCELLED,
    }
    assert ALLOWED_TRANSITIONS[DefaultStatus.CALLED] == {
        DefaultStatus.SERVED,
        DefaultStatus.SKIPPED,
    }
    assert ALLOWED_TRANSITIONS[DefaultStatus.SKIPPED] == {
        DefaultStatus.RE_QUEUED
    }
    # Terminal states
    assert ALLOWED_TRANSITIONS[DefaultStatus.SERVED] == set()
    assert ALLOWED_TRANSITIONS[DefaultStatus.RE_QUEUED] == set()
    assert ALLOWED_TRANSITIONS[DefaultStatus.CANCELLED] == set()


def test_notification_position_thresholds():
    assert NOTIFY_PREPARE_POSITION == 3
    assert NOTIFY_ALMOST_POSITION == 1


def test_default_status_is_str_enum():
    # StrEnum formats to its value (used in transition messages / log rows).
    assert f"{DefaultStatus.SERVED}" == "served"
    assert DefaultStatus.WAITING == "waiting"


def test_exception_status_codes_and_messages():
    cases = [
        (QueueNotFound, 404),
        (StatusNotFound, 404),
        (SettingsNotFound, 404),
        (NoQueueToCall, 404),
        (SettingsNotConfigured, 409),
        (StatusInUse, 409),
        (ProtectedStatus, 409),
        (QueueClosed, 409),
        (OutsideOperatingHours, 409),
        (DailyQuotaExceeded, 409),
        (InvalidStateTransition, 409),
    ]
    for exc_cls, code in cases:
        exc = exc_cls()
        assert exc.status_code == code
        assert exc.message == exc_cls.default_message
        assert isinstance(exc, QueueServiceError)


def test_exception_custom_message_override():
    exc = QueueNotFound("custom message")
    assert exc.message == "custom message"
    assert str(exc) == "custom message"


def test_base_error_default_status_code():
    assert QueueServiceError().status_code == 400
