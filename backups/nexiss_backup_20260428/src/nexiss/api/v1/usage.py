from __future__ import annotations

from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from nexiss.api.deps.auth import AuthContext, require_org_context
from nexiss.db.models.usage_event import UsageEvent
from nexiss.db.session import get_db_session
from nexiss.schemas.usage import UsageMetricSummary, UsageSummaryResponse

router = APIRouter(prefix="/usage", tags=["usage"])


def _normalize_total_cost(value: Decimal | None) -> Decimal | None:
    if value is None:
        return None
    return value


@router.get("/summary", response_model=UsageSummaryResponse)
async def get_usage_summary(
    auth: AuthContext = Depends(require_org_context),
    db: AsyncSession = Depends(get_db_session),
) -> UsageSummaryResponse:
    rows = await db.execute(
        select(
            UsageEvent.metric_type,
            func.sum(UsageEvent.quantity).label("quantity_total"),
            func.sum(UsageEvent.total_cost).label("total_cost"),
        )
        .where(UsageEvent.org_id == auth.active_org_id)
        .group_by(UsageEvent.metric_type)
        .order_by(UsageEvent.metric_type.asc())
    )

    metrics = [
        UsageMetricSummary(
            metric_type=metric_type.value,
            quantity_total=int(quantity_total or 0),
            total_cost=_normalize_total_cost(total_cost),
        )
        for metric_type, quantity_total, total_cost in rows.all()
    ]
    return UsageSummaryResponse(org_id=auth.active_org_id, metrics=metrics)
