import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.lib.exceptions import QueueServiceError
from app.routers import api_router
from app.schemas.response import fail

logger = logging.getLogger(__name__)

app = FastAPI(title="Queue Service API", version="1.0")


def _envelope(status_code: int, message: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content=fail(message).model_dump())


@app.exception_handler(QueueServiceError)
def handle_domain_error(request: Request, exc: QueueServiceError) -> JSONResponse:
    return _envelope(exc.status_code, exc.message)


@app.exception_handler(RequestValidationError)
def handle_validation_error(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "data": exc.errors(),
            "message": "Validation error",
        },
    )


@app.exception_handler(Exception)
def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled error: %s", exc)
    return _envelope(
        status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal server error"
    )


app.include_router(api_router)


@app.get("/")
def read_root():
    return {"success": True, "data": None, "message": "Welcome to the Queue Service API"}
