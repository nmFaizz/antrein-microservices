"""Konfigurasi OpenTelemetry tracing."""
import os


def setup_tracing(service_name: str) -> None:
    """Inisialisasi tracer provider dan exporter ke Jaeger via OTLP."""
    if os.getenv("OTEL_SDK_DISABLED", "").lower() in ("true", "1", "yes"):
        return

    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

    resource = Resource.create({
        "service.name": service_name,
        "service.version": os.getenv("SERVICE_VERSION", "1.0.0"),
        "deployment.environment": os.getenv("ENV", "development"),
    })

    provider = TracerProvider(resource=resource)

    otlp_endpoint = os.getenv(
        "OTEL_EXPORTER_OTLP_ENDPOINT",
        "http://jaeger:4318/v1/traces",
    )
    exporter = OTLPSpanExporter(endpoint=otlp_endpoint)

    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)

    HTTPXClientInstrumentor().instrument()
