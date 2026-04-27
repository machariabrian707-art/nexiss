# Nexiss — Universal Document Intelligence Platform

> Take a photo of any document → Nexiss reads it, classifies it, extracts the data, links it to named entities, and makes it searchable and exportable.

---

## Quick Start (Docker)

```bash
git clone https://github.com/machariabrian707-art/nexiss.git
cd nexiss
cp .env.example .env
docker compose -f infra/docker-compose.dev.yml up -d
alembic upgrade head
uvicorn nexiss.main:app --reload
```

API Docs: http://localhost:8000/docs

---

## Local Development

```bash
pip install -e ".[dev]"
alembic upgrade head
uvicorn nexiss.main:app --reload
pytest
```

---

## Stack

| Layer | Technology |
|-------|------------|
| API | FastAPI + SQLAlchemy (async) |
| DB | PostgreSQL 16 |
| Queue | Celery + Redis |
| OCR | AWS Textract / mock |
| AI Extraction | OpenAI / mock |
| Storage | AWS S3 (signed URLs) |
| Export | openpyxl (Excel) |
| Realtime | WebSocket + Redis pub/sub |
| Billing | Stripe (webhook-ready) |
| Observability | Prometheus + Sentry (optional) |

---

## Build Phases

| Phase | What was built |
|-------|----------------|
| 0 | Scaffolding, config, health |
| 1 | Multi-tenant DB models (orgs, users, docs, usage) |
| 2 | JWT auth, multi-org switching |
| 3 | S3 signed upload/download |
| 4 | Document create/list/get API |
| 5 | Celery background processing, status transitions |
| 6 | Retry, lifecycle observability, OCR+LLM pipeline |
| 7 | Persistent progress tracking (processing_jobs) |
| 8 | WebSocket realtime progress via Redis pub/sub |
| 9 | Internal automation engine (hidden from users) |
| 10 | Analytics queries + daily trend endpoints |
| 11 | Stripe billing (webhook + status) |
| 12 | Prometheus metrics middleware |
| 13 | Document classification (12 categories), entity extraction + fuzzy matching |
| 14 | Export to Excel, Super Admin API, entity review/merge queue |

---

## API Endpoints

### Auth
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/switch-org`
- `GET  /api/v1/auth/me`

### Documents
- `POST /api/v1/documents` — Upload (include `declared_type` for best results)
- `GET  /api/v1/documents` — List all
- `GET  /api/v1/documents/search?q=&doc_type=&entity_name=&status=` — Smart search
- `GET  /api/v1/documents/{id}`
- `GET  /api/v1/documents/{id}/entities` — Named entities in this document
- `POST /api/v1/documents/{id}/process`
- `POST /api/v1/documents/{id}/retry`
- `GET  /api/v1/documents/{id}/progress`

### Export
- `GET /api/v1/export/documents.xlsx?doc_type=medical_healthcare` — Download as Excel

### Analytics
- `GET /api/v1/analytics/overview`
- `GET /api/v1/analytics/daily-processing?days=30`

### Billing
- `GET  /api/v1/billing/status`
- `POST /api/v1/billing/stripe/webhook`

### Super Admin (requires `is_superuser=true`)
- `GET  /api/v1/admin/stats` — Platform-wide counts
- `GET  /api/v1/admin/orgs` — All organisations
- `GET  /api/v1/admin/documents?org_id=&doc_type=` — All documents
- `GET  /api/v1/admin/entity-review` — Low-confidence entity matches needing review
- `POST /api/v1/admin/entity-review/{id}/merge?target_id=` — Merge duplicate entity

### Realtime
- `WS /api/v1/realtime/progress/ws?token=<jwt>&org_id=<uuid>`

---

## Document Categories (declared_type)

| Value | Description |
|-------|-------------|
| `business_financial` | Invoices, receipts, bank statements, payroll |
| `medical_healthcare` | Patient records, prescriptions, lab results |
| `legal` | Contracts, NDAs, court documents |
| `educational` | Certificates, transcripts, research papers |
| `administrative_hr` | CVs, offer letters, performance reviews |
| `logistics_supply_chain` | Bills of lading, delivery notes, customs |
| `government_identity` | Passports, national IDs, permits |
| `media_content` | Articles, scripts, marketing content |
| `technical_data` | Spreadsheets, logs, API docs |
| `image_based` | Scanned docs, receipt photos, handwritten notes |
| `communication` | Emails, meeting minutes, chat exports |
| `other` | Anything else |

---

## Environment Variables

See `.env.example`. Key vars:
- `DATABASE_URL`, `REDIS_URL`
- `S3_BUCKET`, `S3_ACCESS_KEY_ID`, `S3_SECRET_ACCESS_KEY`, `S3_REGION`
- `OPENAI_API_KEY`, `LLM_MODEL`
- `JWT_SECRET_KEY`
- `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`
- `OCR_PROVIDER=mock|textract`, `LLM_PROVIDER=mock|openai`
- `CELERY_TASK_ALWAYS_EAGER=true` (dev mode, no worker needed)
