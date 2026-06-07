from fastapi import APIRouter

from app.routers import (
    queue,
    queue_notification,
    queue_settings,
    queue_status,
)

api_router = APIRouter()
api_router.include_router(queue.router)
api_router.include_router(queue_status.router)
api_router.include_router(queue_settings.router)
api_router.include_router(queue_notification.router)

__all__ = ["api_router"]
