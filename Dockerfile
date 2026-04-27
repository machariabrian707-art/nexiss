# ── Stage 1: builder ─────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /app

# System deps for psycopg2, Pillow, pytesseract
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ libpq-dev libffi-dev libssl-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
RUN pip install --upgrade pip && pip install build && pip install -e . --no-cache-dir

# ── Stage 2: runtime ─────────────────────────────────────────────────────────
FROM python:3.12-slim

WORKDIR /app

# Runtime system deps (tesseract for OCR fallback)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 tesseract-ocr poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy source
COPY src/ ./src/
COPY alembic/ ./alembic/
COPY alembic.ini ./

# Non-root user
RUN useradd -m -u 1001 nexiss
USER nexiss

EXPOSE 8000

CMD ["uvicorn", "nexiss.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
