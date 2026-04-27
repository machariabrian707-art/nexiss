from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class UsageMetricSummary(BaseModel):
    metric_type: str
    quantity_total: int
    total_cost: Decimal | None


class UsageSummaryResponse(BaseModel):
    org_id: UUID
    metrics: list[UsageMetricSummary]
