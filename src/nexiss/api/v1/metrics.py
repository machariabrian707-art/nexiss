from __future__ import annotations

from fastapi import APIRouter

from nexiss.core.metrics import metrics_endpoint

router = APIRouter(tags=["metrics"])


@router.get("/metrics")
def get_metrics():
    return metrics_endpoint()

