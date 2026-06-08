from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import os

from app.db.config import settings
from app.menu.router import router as menu_router
from app.preorder.router import router as preorder_router
from app.core.response import APIResponse, ok, fail
from app.core.metrics import PrometheusMiddleware, metrics_endpoint
from app.core.tracing import setup_tracing
from app.core.logger import get_logger

logger = get_logger(__name__)
setup_tracing(settings.PROJECT_NAME)

app = FastAPI(
    title=settings.PROJECT_NAME,    
    version="1.0.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Prometheus Middleware
app.add_middleware(PrometheusMiddleware)

if os.getenv("OTEL_SDK_DISABLED", "").lower() not in ("true", "1", "yes"):
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    FastAPIInstrumentor.instrument_app(app)

# Exception handler untuk HTTPException (e.g. 404, 401, 403, dll.)
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=fail(message=exc.detail).model_dump()
    )

# Exception handler untuk error validasi input Pydantic / FastAPI
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    errors = exc.errors()
    error_messages = []
    for err in errors:
        loc = " -> ".join(str(item) for item in err.get("loc", []))
        msg = err.get("msg", "Invalid value")
        error_messages.append(f"[{loc}]: {msg}")
    
    combined_message = "Validation Error: " + "; ".join(error_messages)
    return JSONResponse(
        status_code=422,
        content=fail(message=combined_message, data=errors).model_dump()
    )

app.include_router(menu_router)
app.include_router(preorder_router)

@app.get("/metrics")
def metrics():
    return metrics_endpoint()

@app.get("/health", response_model=APIResponse[dict], tags=["Health"])
def health_check():
    return ok({"status": "healthy", "service": settings.PROJECT_NAME}, "Service is healthy")
