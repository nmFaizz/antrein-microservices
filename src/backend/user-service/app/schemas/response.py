from typing import Generic, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """Uniform response envelope returned by every endpoint.

    Shape: ``{ "success": bool, "data": T | null, "message": str }``.
    """

    success: bool = True
    data: Optional[T] = None
    message: str = ""


def ok(data: T = None, message: str = "Success") -> APIResponse[T]:
    """Build a successful response envelope."""
    return APIResponse(success=True, data=data, message=message)


def fail(message: str, data: object = None) -> APIResponse:
    """Build a failed response envelope (used by exception handlers)."""
    return APIResponse(success=False, data=data, message=message)
