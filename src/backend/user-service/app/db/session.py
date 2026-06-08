from contextlib import contextmanager
from typing import Generator

from sqlmodel import Session, create_engine

from app.lib.config import settings

engine = create_engine(settings.DATABASE_URL, echo=True, pool_pre_ping=True)


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """Context-managed session for use in scripts and services."""
    with Session(engine) as session:
        yield session


def get_session() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a database session per request."""
    with Session(engine) as session:
        yield session