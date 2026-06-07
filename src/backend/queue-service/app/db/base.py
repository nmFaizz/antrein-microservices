"""Metadata aggregator for Alembic.

Importing ``app.models`` registers all table models on ``SQLModel.metadata``;
``metadata`` is re-exported here so ``alembic/env.py`` has a single import that
fully populates the autogenerate target.
"""

from sqlmodel import SQLModel

import app.models  # noqa: F401 -- side effect: registers all tables

metadata = SQLModel.metadata

__all__ = ["SQLModel", "metadata"]
