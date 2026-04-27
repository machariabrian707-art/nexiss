# ── Nexiss API + Worker Dockerfile ───────────────────────────
# Multi-stage: builder installs deps, runtime is lean.
# Usage:
#   docker build --target api -t nexiss-api .
#   docker build --target worker -t nexiss-worker .

FROM python:3.11-slim AS base

WORKDIR /app

# System deps: libpq for asyncpg, build tools for compiled packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ── Builder ──────────────────────────────────────────────────
FROM base AS builder

COPY pyproject.toml ./
COPY src ./src

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -e .[observability]

# ── API ──────────────────────────────────────────────────────
FROM builder AS api

COPY alembic.ini ./
COPY alembic ./alembic

EXPOSE 8000

# Run migrations then start API
CMD ["sh", "-c", "alembic upgrade head && uvicorn nexiss.main:app --host 0.0.0.0 --port 8000"]

# ── Worker ───────────────────────────────────────────────────
FROM builder AS worker

CMD ["celery", "-A", "nexiss.worker.celery_app", "worker", "--loglevel=info", "--concurrency=4"]
