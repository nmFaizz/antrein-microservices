import uuid
from datetime import date
from typing import Optional

from sqlmodel import Session, func, select

from app.models.queue import Queue
from app.repositories.base import BaseRepository


class QueueRepository(BaseRepository[Queue]):
    model = Queue

    def list_filtered(
        self,
        *,
        queue_date: Optional[date] = None,
        status_id: Optional[uuid.UUID] = None,
        is_checked_in: Optional[bool] = None,
        offset: int = 0,
        limit: int = 50,
    ) -> list[Queue]:
        statement = select(Queue)
        if queue_date is not None:
            statement = statement.where(Queue.queue_date == queue_date)
        if status_id is not None:
            statement = statement.where(Queue.status_id == status_id)
        if is_checked_in is not None:
            statement = statement.where(Queue.is_checked_in == is_checked_in)
        statement = (
            statement.order_by(Queue.queue_number).offset(offset).limit(limit)
        )
        return list(self.session.exec(statement).all())

    def count_for_date(self, queue_date: date) -> int:
        statement = (
            select(func.count())
            .select_from(Queue)
            .where(Queue.queue_date == queue_date)
        )
        return self.session.exec(statement).one()

    def next_queue_number(self, queue_date: date) -> int:
        """Next sequential number for the day (resets daily)."""
        statement = select(func.max(Queue.queue_number)).where(
            Queue.queue_date == queue_date
        )
        current_max = self.session.exec(statement).one()
        return (current_max or 0) + 1

    def list_waiting_ordered(
        self, queue_date: date, waiting_status_id: uuid.UUID
    ) -> list[Queue]:
        statement = (
            select(Queue)
            .where(Queue.queue_date == queue_date)
            .where(Queue.status_id == waiting_status_id)
            .order_by(Queue.created_at)
        )
        return list(self.session.exec(statement).all())

    def get_next_to_call(
        self, queue_date: date, waiting_status_id: uuid.UUID
    ) -> Optional[Queue]:
        """Earliest waiting ticket, checked-in customers prioritized."""
        statement = (
            select(Queue)
            .where(Queue.queue_date == queue_date)
            .where(Queue.status_id == waiting_status_id)
            .order_by(Queue.is_checked_in.desc(), Queue.created_at)
            .limit(1)
        )
        return self.session.exec(statement).first()

    def position_of(self, queue: Queue, waiting_status_id: uuid.UUID) -> int:
        """Number of waiting tickets ahead of ``queue`` (0 = at the front)."""
        if queue.status_id != waiting_status_id:
            return 0
        statement = (
            select(func.count())
            .select_from(Queue)
            .where(Queue.queue_date == queue.queue_date)
            .where(Queue.status_id == waiting_status_id)
            .where(Queue.created_at < queue.created_at)
        )
        return self.session.exec(statement).one()

    def served_durations_minutes(
        self, queue_date: date, served_status_id: uuid.UUID
    ) -> list[float]:
        """(served_at - called_at) in minutes for today's served tickets."""
        statement = (
            select(Queue)
            .where(Queue.queue_date == queue_date)
            .where(Queue.status_id == served_status_id)
            .where(Queue.called_at.is_not(None))
            .where(Queue.served_at.is_not(None))
        )
        rows = self.session.exec(statement).all()
        return [
            (row.served_at - row.called_at).total_seconds() / 60.0
            for row in rows
        ]
