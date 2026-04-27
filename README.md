# Nexiss — Document Intelligence Platform

## Quick Start (Docker)

```bash
# 1. Clone
git clone https://github.com/rayoovoid3-alt/nexiss.git
cd nexiss

# 2. Copy and fill in env
cp .env.example .env

# 3. Start everything
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## Local Development

### Backend
```bash
pip install -e ".[dev]"
alembic upgrade head
uvicorn nexiss.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## Stack

| Layer | Technology |
|-------|------------|
| API | FastAPI + SQLAlchemy (async) |
| DB | PostgreSQL 16 |
| Queue | Celery + Redis |
| OCR | AWS Textract + pytesseract fallback |
| AI | OpenAI GPT-4o (extraction) |
| Storage | AWS S3 (signed URLs) |
| Frontend | React 18 + Vite + TypeScript + Tailwind |
| Deploy | Docker Compose / Kubernetes |

---

## Project Structure

```
nexiss/
├── src/nexiss/           ← FastAPI backend
│   ├── api/v1/           ← REST endpoints
│   ├── db/models/        ← SQLAlchemy models
│   ├── services/         ← OCR, AI, storage, analytics
│   ├── worker/           ← Celery tasks
│   └── automation/       ← Internal triggers & workflows
├── frontend/             ← React app
│   ├── src/pages/        ← All pages (app + admin)
│   ├── src/components/   ← Reusable UI
│   ├── src/api/          ← API client layer
│   └── src/stores/       ← Zustand state
├── infra/                ← Docker / K8s configs
├── scripts/              ← Review queue scripts
└── docker-compose.yml    ← Full local stack
```

---

## Environment Variables

See `.env.example` for all required variables:
- `DATABASE_URL`
- `REDIS_URL`
- `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` / `AWS_S3_BUCKET`
- `OPENAI_API_KEY`
- `SECRET_KEY` (JWT signing)
- `STRIPE_SECRET_KEY` (billing)
