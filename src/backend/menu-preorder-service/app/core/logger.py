import logging
import os
from pythonjsonlogger import jsonlogger
from opentelemetry import trace
import logging_loki


class TraceContextFilter(logging.Filter):
    """Inject trace_id & span_id ke setiap log record (jika ada active span)."""

    def filter(self, record: logging.LogRecord) -> bool:
        span = trace.get_current_span()
        ctx = span.get_span_context()
        if ctx.is_valid:
            record.trace_id = format(ctx.trace_id, "032x")
            record.span_id = format(ctx.span_id, "016x")
        else:
            record.trace_id = None
            record.span_id = None
        return True


def get_logger(name: str) -> logging.Logger:
    """Buat logger dengan dua handler: console (JSON) dan Loki."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))
    logger.addFilter(TraceContextFilter())

    service_name = os.getenv("OTEL_SERVICE_NAME", "Menu Preorder Service")

    json_format = "%(asctime)s %(levelname)s %(name)s %(message)s %(trace_id)s %(span_id)s"
    formatter = jsonlogger.JsonFormatter(
        json_format,
        rename_fields={"levelname": "level", "asctime": "timestamp"},
    )

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    logger.addHandler(console)

    loki_url = os.getenv("LOKI_URL", "http://loki:3100/loki/api/v1/push")
    try:
        loki_handler = logging_loki.LokiHandler(
            url=loki_url,
            tags={"service": service_name, "service_name": service_name},
            version="1",
        )
        loki_handler.setFormatter(formatter)
        logger.addHandler(loki_handler)
    except Exception as e:
        print(f"[logger] Loki not available: {e}")

    logger.propagate = False
    return logger
