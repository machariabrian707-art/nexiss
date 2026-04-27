# Nexiss Backend

Production-grade multi-tenant SaaS backend foundation built with FastAPI.

## Phase 0 scope

- Project scaffolding with clean architecture layout
- Dependency and tooling configuration
- Environment-driven settings system
- Logging baseline and health API
- Async database/session and Celery initialization skeletons

## Phase 1 scope

- Core multi-tenant database models for organizations, users, memberships, documents, and usage
- Alembic migration scaffolding and initial migration

## Phase 2 scope

- JWT authentication (register, login, switch org, current user)
- Password hashing with bcrypt via passlib
- Multi-tenant org authorization dependency with `X-Org-Id` enforcement

## Phase 3 scope

- S3 signed upload and download URL endpoints
- Strict org-scoped storage keys
- Download signing allowed only for documents in active org

## Local setup

1. Create a virtual environment and activate it.
2. Install dependencies:
   - `pip install -e .[dev]`
3. Copy environment template:
   - `copy .env.example .env` (Windows PowerShell)
4. Start API:
   - `uvicorn nexiss.main:app --reload`
5. Run tests:
   - `pytest`

## Local infrastructure (PostgreSQL + Redis)

- Start dependencies with Docker:
  - `docker compose -f infra/docker-compose.dev.yml up -d`
- Stop dependencies:
  - `docker compose -f infra/docker-compose.dev.yml down`
- Default local endpoints:
  - PostgreSQL: `localhost:5432` (`postgres/postgres`, db `nexiss`)
  - Redis: `localhost:6379`

## Database migration

- Run initial schema migration:
  - `alembic upgrade head`

If Postgres is not running, migrations fail by design. Start Docker dependencies first.

## Auth endpoints

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/switch-org`
- `GET /api/v1/auth/me`
- `GET /api/v1/tenancy/context` (requires `Authorization` and `X-Org-Id`)

## Storage endpoints

- `POST /api/v1/storage/signed-upload`
- `POST /api/v1/storage/signed-download`

## Phase 4 scope

- Document creation API for uploaded files
- Org-isolated document list and detail retrieval

## Phase 5 scope

- Background document processing trigger (`Celery`)
- Status transitions (`uploaded` -> `processing` -> `completed|failed`)
- Stub extraction payload population and usage event tracking

## Phase 6 scope

- Retry endpoint for failed document processing jobs
- Document lifecycle observability (`processing_attempts`, `last_error`)
- Org-scoped usage summary API grouped by metric type
- Follow-up migration for document lifecycle fields (`20260427_0002`)
- OCR extraction layer (`services/ai/ocr_service.py`)
- LLM extraction layer (`services/ai/llm_extraction_service.py`)
- Orchestrated processing pipeline (`services/ai/pipeline.py`) used by Celery task
- LLM token usage events for billing readiness (`llm_tokens_input`, `llm_tokens_output`)

## Phase 7 scope

- Persistent progress tracking table (`processing_jobs`) with org isolation
- Job lifecycle states (`queued`, `running`, `completed`, `failed`)
- Step-level progress updates from Celery processing task
- Document progress polling endpoint returning latest job state

## Phase 8 scope

- WebSocket endpoint for real-time document progress events
- Redis pub/sub event transport for cross-process progress fan-out
- Org-scoped channel isolation for realtime subscriptions
- Celery-to-WebSocket bridge via published progress events

## Phase 9 scope

- Internal-only automation engine (`services/automation/engine.py`)
- Tenant-scoped automation rule and execution run tables
- Automation trigger integration in post-document-processing worker flow
- No public API exposure for automation components

## Phase 10 scope

- Tenant-safe analytics query service (`services/analytics/queries.py`)
- Analytics overview endpoint for processing + token aggregates
- Daily processing trend endpoint (documents/pages)
- Query composition using org-scoped filters only

## Phase 11 scope

- Stripe-ready billing data model (customers + subscriptions)
- Stripe webhook verification + ingestion endpoint
- Tenant-safe billing status endpoint (`/billing/status`)
- Billing is keyed by `org_id` and designed for Stripe metadata linkage

## Phase 12 scope

- Prometheus metrics endpoint (`/metrics`)
- HTTP request metrics middleware (bounded cardinality)
- Celery task outcome metrics
- Optional external observability provider (disabled unless configured)

## Document endpoints

- `POST /api/v1/documents`
- `GET /api/v1/documents`
- `GET /api/v1/documents/{document_id}`
- `POST /api/v1/documents/{document_id}/process`
- `POST /api/v1/documents/{document_id}/retry`
- `GET /api/v1/documents/{document_id}/progress`

## Realtime endpoint

- `WS /api/v1/realtime/progress/ws?token=<jwt>&org_id=<org_uuid>`

## Usage endpoints

- `GET /api/v1/usage/summary`

## Analytics endpoints

- `GET /api/v1/analytics/overview`
- `GET /api/v1/analytics/daily-processing?days=30`

## Billing endpoints

- `GET /api/v1/billing/status`
- `POST /api/v1/billing/stripe/webhook`

## Metrics endpoint

- `GET /api/v1/metrics`

## Optional local dev toggle

- Set `CELERY_TASK_ALWAYS_EAGER=true` in `.env` to run Celery tasks inline without a worker.
- Phase 6 AI pipeline defaults to mock providers via `.env`:
  - `OCR_PROVIDER=mock`
  - `LLM_PROVIDER=mock`
  - `LLM_MODEL=mock-extractor-v1`
