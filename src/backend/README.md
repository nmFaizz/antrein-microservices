# Antrein Backend Services & Port Mapping

This document lists all active services, their local port configurations, and quick links to access their user interfaces, documentation, and endpoints.

## 🚀 Services & Port List

| Service Name | Container Port | Localhost Port | External URLs / UI Links | Description |
| :--- | :---: | :---: | :--- | :--- |
| **Menu Preorder Service** | `8000` | `8000` | [Docs (Swagger)](http://localhost:8000/docs)  | FastAPI microservice for menu and preorder management. |
| **Queue Service** | `8000` | `8001` | [Docs (Swagger)](http://localhost:8001/docs)  | Microservice handling the preorder processing queues. |
| **Grafana** | `3000` | `3000` | [Grafana Dashboard](http://localhost:3000) | Observability visualization platform (preconfigured dashboards and datasources). |
| **Jaeger** | `16686` <br> `4317` <br> `4318` | `16686` <br> `4317` <br> `4318` | [Jaeger UI](http://localhost:16686)  | Distributed tracing backend (receives traces over gRPC/HTTP OTLP). |
| **Prometheus** | `9090` | `9090` | [Prometheus UI](http://localhost:9090)  | Systems monitoring and alerting toolkit (scrapes service metrics). |
| **Loki** | `3100` | `3100` | [Loki API Status](http://localhost:3100/ready)  | Log aggregation engine. |


## 🛠️ Observability Integration Flow

1. **Metrics**: `menu-preorder-service` exposes metrics on `/metrics`. **Prometheus** scrapes it and exposes its data to **Grafana**.
2. **Traces**: `menu-preorder-service` sends traces to **Jaeger** via OTLP HTTP (`http://jaeger:4318/v1/traces`).
3. **Logs**: `menu-preorder-service` pushes logs to **Loki** using `python-logging-loki` (`http://loki:3100/loki/api/v1/push`).
4. **Grafana Console**: Connects all of them. You can search trace IDs directly from Loki logs in Grafana.
