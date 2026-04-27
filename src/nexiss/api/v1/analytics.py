from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from nexiss.api.deps.auth import AuthContext, require_org_context
from nexiss.db.session import get_db_session
from nexiss.schemas.analytics import (
    AnalyticsDailyProcessingResponse,
    AnalyticsOverviewResponse,
    DailyProcessingPoint,
)
from nexiss.services.analytics.queries import load_analytics_overview, load_daily_processing_stats

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/overview", response_model=AnalyticsOverviewResponse)
async def get_analytics_overview(
    auth: AuthContext = Depends(require_org_context),
    db: AsyncSession = Depends(get_db_session),
) -> AnalyticsOverviewResponse:
    overview = await load_analytics_overview(db, auth.active_org_id)
    return AnalyticsOverviewResponse(
        org_id=auth.active_org_id,
        total_documents_processed=overview.total_documents_processed,
        total_pages_processed=overview.total_pages_processed,
        total_llm_tokens_input=overview.total_llm_tokens_input,
        total_llm_tokens_output=overview.total_llm_tokens_output,
        processing_success_count=overview.processing_success_count,
        processing_failed_count=overview.processing_failed_count,
    )


@router.get("/daily-processing", response_model=AnalyticsDailyProcessingResponse)
async def get_daily_processing(
    days: int = Query(default=30, ge=1, le=365),
    auth: AuthContext = Depends(require_org_context),
    db: AsyncSession = Depends(get_db_session),
) -> AnalyticsDailyProcessingResponse:
    points = await load_daily_processing_stats(db, auth.active_org_id, days=days)
    return AnalyticsDailyProcessingResponse(
        org_id=auth.active_org_id,
        points=[
            DailyProcessingPoint(
                day=point.day,
                documents_processed=point.documents_processed,
                pages_processed=point.pages_processed,
            )
            for point in points
        ],
    )
