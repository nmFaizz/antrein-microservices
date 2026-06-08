import os

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.logger import get_logger
from app.core.metrics import PrometheusMiddleware, metrics_endpoint
from app.core.tracing import setup_tracing
from app.lib.config import settings
from app.lib.exceptions import UserServiceError
from app.routers import api_router
from app.schemas.response import fail

logger = get_logger(__name__)
setup_tracing(settings.PROJECT_NAME)

app = FastAPI(title="User Service API", version="1.0")

# Prometheus middleware: catat metrics untuk setiap request HTTP.
app.add_middleware(PrometheusMiddleware)

if os.getenv("OTEL_SDK_DISABLED", "").lower() not in ("true", "1", "yes"):
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

    FastAPIInstrumentor.instrument_app(app)


def _envelope(status_code: int, message: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content=fail(message).model_dump())


@app.exception_handler(UserServiceError)
def handle_domain_error(request: Request, exc: UserServiceError) -> JSONResponse:
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
    return {"success": True, "data": None, "message": "Welcome to the User Service API"}


@app.get("/metrics")
def metrics():
    return metrics_endpoint()
