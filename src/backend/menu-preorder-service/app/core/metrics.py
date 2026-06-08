import time
from prometheus_client import Counter, Histogram, CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

registry = CollectorRegistry()

http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    labelnames=["method", "route", "status_code"],
    registry=registry,
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    labelnames=["method", "route", "status_code"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10),
    registry=registry,
)


class PrometheusMiddleware(BaseHTTPMiddleware):
    """Catat metrics untuk setiap request HTTP."""

    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        response: Response = await call_next(request)
        duration = time.perf_counter() - start

        route = request.scope.get("route")
        route_path = route.path if route else request.url.path

        labels = {
            "method": request.method,
            "route": route_path,
            "status_code": str(response.status_code),
        }
        http_requests_total.labels(**labels).inc()
        http_request_duration_seconds.labels(**labels).observe(duration)
        return response


def metrics_endpoint() -> Response:
    """Endpoint yang akan di-scrape Prometheus."""
    return Response(content=generate_latest(registry), media_type=CONTENT_TYPE_LATEST)
