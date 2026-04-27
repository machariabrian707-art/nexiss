from __future__ import annotations

import time
from typing import Callable

from fastapi import Request, Response
from prometheus_client import Counter, Histogram, REGISTRY, CONTENT_TYPE_LATEST, generate_latest


http_requests_total = Counter(
    "nexiss_http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status_code"],
)
http_request_duration_seconds = Histogram(
    "nexiss_http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "path"],
)

celery_tasks_total = Counter(
    "nexiss_celery_tasks_total",
    "Total Celery task outcomes",
    ["task_name", "status"],
)


def metrics_endpoint() -> Response:
    data = generate_latest(REGISTRY)
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)


def _normalize_path(path: str) -> str:
    # Keep metrics cardinality bounded.
    if path.startswith("/api/"):
        return path
    return path


async def metrics_middleware(request: Request, call_next: Callable) -> Response:
    start = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start

    path = _normalize_path(request.url.path)
    http_request_duration_seconds.labels(request.method, path).observe(duration)
    http_requests_total.labels(request.method, path, str(response.status_code)).inc()
    return response

