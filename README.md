# Antrein Microservices

Queue management and food pre-ordering system for restaurants and cafeterias. Customers browse menus, place pre-orders, receive queue tickets, and get notified when their order is ready. Admins manage menus, queue configurations, and serve/skip/call customers in real time.

Built as three independent Python microservices with a Next.js frontend, orchestrated via Docker Compose, with a full observability stack.

---

## 1. Tech Stack

### Backend (Python 3.11)
| Service | Framework | Database | Auth |
|---|---|---|---|
| `user-service` | FastAPI 0.136.3 | PostgreSQL 16 | JWT + bcrypt |
| `menu-preorder-service` | FastAPI 0.136.3 | PostgreSQL 16 | JWT |
| `queue-service` | FastAPI 0.136.3 | PostgreSQL 16 | JWT |

**Shared backend tooling:** SQLModel/SQLAlchemy, Alembic, Pydantic v2, OpenTelemetry, Prometheus metrics, Loki logging, pytest (with 90% coverage target on queue-service).

### Frontend
- **Next.js 16** + React 19 + TypeScript 5
- **Tailwind CSS 4** (styling)
- **TanStack React Query 5** (server state)
- **TanStack React Table** (data tables)
- **Axios** (HTTP client)
- **react-hook-form + Zod** (forms/validation)
- **Biome 2** (linter + formatter)

### Infrastructure
- **Nginx** — API gateway routing to all 3 services
- **Docker Compose** — full stack orchestration
- **PostgreSQL 16** × 3 (one per service)
- **Prometheus** — metrics scraping
- **Grafana** — pre-provisioned RED-metrics dashboards
- **Loki** — log aggregation
- **Jaeger** — distributed tracing (OTLP HTTP)

---

## 2. About the Project

**Antrein** (from Indonesian _antre_ — "to queue") is a full-stack queue management platform. Customers can:

- Browse the menu and place pre-orders
- Receive a queue ticket with position and estimated time
- Check in when they arrive
- Get notified when called, served, or skipped

Admins can:

- Manage menu items (CRUD, availability toggle)
- Call next customer, mark served, skip, or requeue
- Configure queue settings (prefix, grace period, avg serve time, operating hours)
- Customize queue statuses (name + color)
- View all preorders and queue logs

### Architecture

```
┌──────────┐     ┌─────────────────────────────────────┐
│  Next.js  │────▶│           Nginx Gateway             │
│ (Port 3000)│    │              (Port 8080)              │
└──────────┘     └──┬────────────┬──────────────┬───────┘
                    │            │              │
                    ▼            ▼              ▼
            ┌──────────┐ ┌──────────────┐ ┌────────────┐
            │  User    │ │ Menu-Preorder│ │   Queue    │
            │ Service  │ │   Service    │ │  Service   │
            │ :8002    │ │   :8000      │ │  :8001     │
            ├──────────┤ ├──────────────┤ ├────────────┤
            │PostgreSQL│ │ PostgreSQL   │ │ PostgreSQL │
            └──────────┘ └──────────────┘ └────────────┘
                    ▲            │  ▲              │
                    │            │  │ (HTTP/httpx) │
                    └────────────┘  └──────────────┘
```

Each service follows a **repository → service → router** pattern with FastAPI dependency injection. Inter-service communication uses HTTP via `httpx`.

---

## 3. Setup

### Prerequisites

- Docker & Docker Compose
- Node.js 20+ and pnpm (for frontend dev)
- Python 3.11+ (for backend dev outside Docker)

### Quick Start (Full Stack)

```bash
# 1. Clone and enter the project
git clone <repo-url>
cd antr ein-microservices

# 2. Create environment file
cp src/backend/user-service/.env.example src/backend/.env
# Edit src/backend/.env — at minimum set JWT_SECRET_KEY
```

`.env` reference:

```
USER_DB_PORT=5432
USER_DB_NAME=user_db
USER_DB_USER=postgres
USER_DB_PASSWORD=postgres

JWT_SECRET_KEY=<run: python -c "import secrets; print(secrets.token_urlsafe(32))">
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60

MENU_PREORDER_DB_HOST=menu-preorder-db
MENU_PREORDER_DB_PORT=5433
MENU_PREORDER_DB_NAME=menu_preorder_db
MENU_PREORDER_DB_USER=postgres
MENU_PREORDER_DB_PASSWORD=postgres

QUEUE_DB_PORT=5434
QUEUE_DB_NAME=queue_service_db
QUEUE_DB_USER=postgres
QUEUE_DB_PASSWORD=postgres
```

```bash
# 3. Start all backend services
cd src/backend
docker-compose up --build
```

On startup each service runs `alembic upgrade head` + database seeder, then starts Uvicorn.

```bash
# 4. (Separate terminal) Start the frontend
cd src/frontend
pnpm install
pnpm dev
```

### Available Endpoints

| URL | Service |
|---|---|
| `http://localhost:8000/docs` | Menu-Preorder API (Swagger) |
| `http://localhost:8001/docs` | Queue API (Swagger) |
| `http://localhost:8002/docs` | User API (Swagger) |
| `http://localhost:8080` | Nginx Gateway |
| `http://localhost:3000` | Grafana |
| `http://localhost:9090` | Prometheus |
| `http://localhost:16686` | Jaeger UI |

### Default Seed Accounts

| Username | Password | Role |
|---|---|---|
| `user1` / `user2` / `user3` | `password123` | user |
| `admin1` / `admin2` / `admin3` | `adminpass123` | admin |

### Running Tests

```bash
# user-service
cd src/backend/user-service
pip install -r requirements.txt
pytest

# queue-service (90% coverage required)
cd src/backend/queue-service
pip install -r requirements.txt -r requirements-dev.txt
pytest

# menu-preorder-service
cd src/backend/menu-preorder-service
pip install -r requirements.txt
pytest

# frontend
cd src/frontend
pnpm test
```

---

## 4. Contributing

### Code Style

- **Python:** Follow existing patterns — FastAPI routers, service layer, repository pattern, Pydantic v2 schemas
- **TypeScript:** Biome is configured (`biome.json`). Run `pnpm lint` / `pnpm format` before committing
- **API Responses:** All endpoints return the envelope `{ success: bool, data: T | null, message: string }`

### Architecture Principles

- **Repository Pattern** — `BaseRepository[ModelT]` with `get`, `list`, `add`, `delete`
- **Service Layer** — Business logic in services; services own the transaction
- **Auth** — Two roles (`admin` / `user`); protect endpoints with `require_admin` dependency
- **Inter-service calls** — Use `httpx` with a dedicated client class

### Branching & PRs

- Create feature branches from `main`
- Keep PRs focused on a single concern
- Ensure tests pass and coverage meets thresholds before merging

### Project Structure

```
src/
├── backend/
│   ├── docker-compose.yml
│   ├── user-service/          # Auth & user management
│   ├── menu-preorder-service/  # Menu & preorder CRUD
│   └── queue-service/          # Queue lifecycle & settings
├── frontend/
│   └── src/
│       ├── features/           # Feature modules (auth, menu, queue, ...)
│       ├── components/ui/      # Reusable UI components
│       ├── lib/                # Shared utilities
│       └── providers/          # React context providers
└── ...
```
