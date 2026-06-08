import uuid
from datetime import date, timedelta
from statistics import mean
from typing import Optional

from sqlmodel import Session

from app.lib.constants import (
    ALLOWED_TRANSITIONS,
    NOTIFY_ALMOST_POSITION,
    NOTIFY_PREPARE_POSITION,
    DefaultStatus,
)
from app.lib.exceptions import (
    DailyQuotaExceeded,
    InvalidStateTransition,
    NoQueueToCall,
    OutsideOperatingHours,
    QueueClosed,
    QueueNotFound,
)
from app.models.enums import NotificationType, TriggerType
from app.models.queue import Queue
from app.models.queue_settings import QueueSettings
from app.models.mixins import utcnow as _now
from app.models.queue_status_log import QueueStatusLog
from app.repositories.queue import QueueRepository
from app.repositories.queue_notification import QueueNotificationRepository
from app.repositories.queue_settings import QueueSettingsRepository
from app.repositories.queue_status_log import QueueStatusLogRepository
from app.schemas.queue import (
    CallNextRequest,
    CancelRequest,
    QueueCreate,
    QueueRead,
    RequeueRequest,
    ServeRequest,
    SkipRequest,
)
from app.clients.preorder_service import PreorderServiceClient
from app.services.notification_service import NotificationService
from app.services.status_resolver import StatusResolver


class QueueService:
    """Orchestrates the queue lifecycle (one transaction per operation)."""

    def __init__(
        self,
        session: Session,
        queue_repo: QueueRepository,
        settings_repo: QueueSettingsRepository,
        log_repo: QueueStatusLogRepository,
        notification_repo: QueueNotificationRepository,
        resolver: StatusResolver,
        notification_service: NotificationService,
        preorder_client: PreorderServiceClient,
    ) -> None:
        self.session = session
        self.queue_repo = queue_repo
        self.settings_repo = settings_repo
        self.log_repo = log_repo
        self.notification_repo = notification_repo
        self.resolver = resolver
        self.notification_service = notification_service
        self.preorder_client = preorder_client

    def create_queue(self, data: QueueCreate) -> QueueRead:
        settings = self._require_settings()
        if not settings.is_queue_open:
            raise QueueClosed()
        self._assert_within_hours(settings)

        queue_date = data.queue_date or date.today()
        if self.queue_repo.count_for_date(queue_date) >= settings.max_queue_per_day:
            raise DailyQuotaExceeded()

        waiting_id = self.resolver.id_for(DefaultStatus.WAITING)
        queue = Queue(
            user_id=data.customer_id,
            preorder_id=data.preorder_id,
            queue_number=self.queue_repo.next_queue_number(queue_date),
            queue_date=queue_date,
            status_id=waiting_id,
        )
        ahead = self.queue_repo.position_of(queue, waiting_id)
        queue.estimated_time = _now() + timedelta(
            minutes=ahead * settings.avg_serve_time_mins
        )
        self.queue_repo.add(queue)
        self._log(queue, None, DefaultStatus.WAITING, None, TriggerType.SYSTEM)
        self.notification_service.create_and_dispatch(
            queue, NotificationType.CONFIRMATION
        )
        self.session.commit()
        return self._to_read(queue)

    def check_in(self, queue_id: uuid.UUID) -> QueueRead:
        queue = self._get_or_404(queue_id)
        queue.is_checked_in = True
        queue.checked_in_at = _now()
        self.queue_repo.add(queue)
        current = self.resolver.name_for(queue.status_id)
        self._log(
            queue,
            current,
            current,
            queue.user_id,
            TriggerType.CUSTOMER,
            notes="Customer checked in",
        )
        self.session.commit()
        return self._to_read(queue)

    def call_next(self, data: CallNextRequest, admin_id: uuid.UUID) -> QueueRead:
        self._require_settings()
        queue_date = data.queue_date or date.today()
        waiting_id = self.resolver.id_for(DefaultStatus.WAITING)
        queue = self.queue_repo.get_next_to_call(queue_date, waiting_id)
        if queue is None:
            raise NoQueueToCall()

        self._transition(queue, DefaultStatus.CALLED)
        queue.called_at = _now()
        queue.called_by = admin_id
        self._log(
            queue,
            DefaultStatus.WAITING,
            DefaultStatus.CALLED,
            admin_id,
            TriggerType.ADMIN,
        )
        self.notification_service.create_and_dispatch(
            queue, NotificationType.CALLED
        )
        self._emit_position_notifications(queue_date)
        self.session.commit()
        read = self._to_read(queue)
        self._sync_preorder(queue, read)
        return read

    def skip(self, queue_id: uuid.UUID, data: SkipRequest, admin_id: Optional[uuid.UUID] = None) -> QueueRead:
        queue = self._get_or_404(queue_id)
        current = self.resolver.name_for(queue.status_id)
        self._transition(queue, DefaultStatus.SKIPPED)
        queue.skipped_by = admin_id
        self._log(
            queue,
            current,
            DefaultStatus.SKIPPED,
            admin_id,
            data.trigger_type,
            notes=data.notes,
        )
        self.notification_service.create_and_dispatch(
            queue, NotificationType.SKIPPED
        )
        self._emit_position_notifications(queue.queue_date)
        self.session.commit()
        read = self._to_read(queue)
        self._sync_preorder(queue, read)
        return read

    def serve(self, queue_id: uuid.UUID, data: ServeRequest, admin_id: uuid.UUID) -> QueueRead:
        queue = self._get_or_404(queue_id)
        self._transition(queue, DefaultStatus.SERVED)
        queue.served_at = _now()
        queue.served_by = admin_id
        self._log(
            queue,
            DefaultStatus.CALLED,
            DefaultStatus.SERVED,
            admin_id,
            TriggerType.ADMIN,
        )
        self._recompute_avg_serve_time(queue.queue_date)
        self._emit_position_notifications(queue.queue_date)
        self.session.commit()
        read = self._to_read(queue)
        self._sync_preorder(queue, read, preorder_status="confirmed")
        return read

    def requeue(self, queue_id: uuid.UUID, data: RequeueRequest, admin_id: uuid.UUID) -> QueueRead:
        source = self._get_or_404(queue_id)
        # Mark the original ticket as re-queued (skipped -> re_queued).
        self._transition(source, DefaultStatus.RE_QUEUED)
        self._log(
            source,
            DefaultStatus.SKIPPED,
            DefaultStatus.RE_QUEUED,
            admin_id,
            TriggerType.ADMIN,
        )

        settings = self._require_settings()
        waiting_id = self.resolver.id_for(DefaultStatus.WAITING)
        new_queue = Queue(
            user_id=source.user_id,
            preorder_id=source.preorder_id,
            queue_number=self.queue_repo.next_queue_number(source.queue_date),
            queue_date=source.queue_date,
            status_id=waiting_id,
            is_requeued=True,
            original_queue_id=source.id,
        )
        ahead = self.queue_repo.position_of(new_queue, waiting_id)
        new_queue.estimated_time = _now() + timedelta(
            minutes=ahead * settings.avg_serve_time_mins
        )
        self.queue_repo.add(new_queue)
        self._log(
            new_queue,
            None,
            DefaultStatus.WAITING,
            admin_id,
            TriggerType.ADMIN,
            notes=f"Re-queued from {source.queue_number}",
        )
        self.notification_service.create_and_dispatch(
            new_queue, NotificationType.REQUEUED
        )
        self.session.commit()
        read = self._to_read(new_queue)
        self._sync_preorder(new_queue, read)
        return read

    def cancel(self, queue_id: uuid.UUID, data: CancelRequest, customer_id: uuid.UUID) -> QueueRead:
        queue = self._get_or_404(queue_id)
        current = self.resolver.name_for(queue.status_id)
        self._transition(queue, DefaultStatus.CANCELLED)
        queue.cancelled_at = _now()
        self._log(
            queue,
            current,
            DefaultStatus.CANCELLED,
            customer_id,
            TriggerType.CUSTOMER,
        )
        self._emit_position_notifications(queue.queue_date)
        self.session.commit()
        read = self._to_read(queue)
        self._sync_preorder(queue, read, preorder_status="cancelled")
        return read

    # ------------------------------------------------------------------ #
    # Reads
    # ------------------------------------------------------------------ #
    def get(self, queue_id: uuid.UUID) -> QueueRead:
        return self._to_read(self._get_or_404(queue_id))

    def list(
        self,
        *,
        queue_date: Optional[date],
        status_id: Optional[uuid.UUID],
        is_checked_in: Optional[bool],
        offset: int,
        limit: int,
    ) -> list[QueueRead]:
        queues = self.queue_repo.list_filtered(
            queue_date=queue_date,
            status_id=status_id,
            is_checked_in=is_checked_in,
            offset=offset,
            limit=limit,
        )
        return [self._to_read(q) for q in queues]

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    def _get_or_404(self, queue_id: uuid.UUID) -> Queue:
        queue = self.queue_repo.get(queue_id)
        if queue is None:
            raise QueueNotFound()
        return queue

    def _require_settings(self) -> QueueSettings:
        from app.lib.exceptions import SettingsNotConfigured

        settings = self.settings_repo.get_active()
        if settings is None:
            raise SettingsNotConfigured()
        return settings

    @staticmethod
    def _assert_within_hours(settings: QueueSettings) -> None:
        if settings.open_time is None or settings.close_time is None:
            return
        now_t = _now().time()
        if not (settings.open_time <= now_t <= settings.close_time):
            raise OutsideOperatingHours()

    def _transition(self, queue: Queue, target: str) -> None:
        current = self.resolver.name_for(queue.status_id)
        if target not in ALLOWED_TRANSITIONS.get(current, set()):
            raise InvalidStateTransition(
                f"Cannot move queue from '{current}' to '{target}'"
            )
        queue.status_id = self.resolver.id_for(target)
        self.queue_repo.add(queue)

    def _log(
        self,
        queue: Queue,
        previous_status: Optional[str],
        new_status: str,
        triggered_by: Optional[uuid.UUID],
        trigger_type: TriggerType,
        notes: Optional[str] = None,
    ) -> None:
        self.log_repo.add(
            QueueStatusLog(
                queue_id=queue.id,
                previous_status=previous_status,
                new_status=new_status,
                triggered_by=triggered_by,
                trigger_type=trigger_type,
                notes=notes,
            )
        )

    def _emit_position_notifications(self, queue_date: date) -> None:
        waiting_id = self.resolver.id_for(DefaultStatus.WAITING)
        waiting = self.queue_repo.list_waiting_ordered(queue_date, waiting_id)
        for ahead, queue in enumerate(waiting):
            if ahead == NOTIFY_PREPARE_POSITION:
                self._maybe_notify(queue, NotificationType.PREPARE)
            elif ahead == NOTIFY_ALMOST_POSITION:
                self._maybe_notify(queue, NotificationType.ALMOST)

    def _maybe_notify(
        self, queue: Queue, notification_type: NotificationType
    ) -> None:
        if self.notification_repo.exists_for_queue_type(
            queue.id, notification_type
        ):
            return
        self.notification_service.create_and_dispatch(queue, notification_type)

    def _recompute_avg_serve_time(self, queue_date: date) -> None:
        served_id = self.resolver.id_for(DefaultStatus.SERVED)
        durations = self.queue_repo.served_durations_minutes(
            queue_date, served_id
        )
        if not durations:
            return
        settings = self._require_settings()
        settings.avg_serve_time_mins = max(1, round(mean(durations)))
        self.settings_repo.add(settings)

    def _sync_preorder(
        self, queue: Queue, read: QueueRead, preorder_status: Optional[str] = None
    ) -> None:
        """Best-effort push of the queue snapshot/status to the preorder."""
        if queue.preorder_id is None:
            return
        snapshot = {
            "id": str(read.id),
            "queue_number": read.queue_number,
            "position": read.current_position,
            "estimated_time": (
                read.estimated_time.isoformat()
                if read.estimated_time is not None
                else None
            ),
            "status": read.status_name,
        }
        self.preorder_client.sync(queue.preorder_id, snapshot, preorder_status)

    def _to_read(self, queue: Queue) -> QueueRead:
        waiting_id = self.resolver.id_for(DefaultStatus.WAITING)
        position = self.queue_repo.position_of(queue, waiting_id)
        settings = self.settings_repo.get_active()
        avg = settings.avg_serve_time_mins if settings else 0
        read = QueueRead(
            **queue.model_dump(),
            status_name=self.resolver.name_for(queue.status_id),
            current_position=position,
            estimated_wait_minutes=position * avg,
        )
        # Enrich with preorder data (best-effort).
        if queue.preorder_id is not None:
            read.preorder = self.preorder_client.get_preorder(queue.preorder_id)
        return read
