from dataclasses import dataclass

from fastapi import Query


@dataclass
class PaginationParams:
    """Reusable offset/limit pagination dependency."""

    offset: int = 0
    limit: int = 50


def pagination_params(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
) -> PaginationParams:
    return PaginationParams(offset=offset, limit=limit)
