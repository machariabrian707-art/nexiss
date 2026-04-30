from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from nexiss.db.models.processing_job import ProcessingJob, ProcessingJobStatus
from nexiss.db.models.usage_event import UsageEvent, UsageMetricType


@dataclass(slots=True)
class AnalyticsOverview:
    total_documents_processed: int
    total_pages_processed: int
    total_llm_tokens_input: int
    total_llm_tokens_output: int
    processing_success_count: int
    processing_failed_count: int


@dataclass(slots=True)
class DailyProcessingStat:
    day: datetime
    documents_processed: int
    pages_processed: int


async def load_analytics_overview(db: AsyncSession, org_id: UUID) -> AnalyticsOverview:
    usage_rows = await db.execute(
        select(
            UsageEvent.metric_type,
            func.sum(UsageEvent.quantity).label("quantity_total"),
        ).where(UsageEvent.org_id == org_id).group_by(UsageEvent.metric_type)
    )
    metric_totals = {metric.value: int(total or 0) for metric, total in usage_rows.all()}

    status_rows = await db.execute(
        select(
            ProcessingJob.status,
            func.count(ProcessingJob.id).label("status_count"),
        ).where(ProcessingJob.org_id == org_id).group_by(ProcessingJob.status)
    )
    status_counts = {status.value: int(total or 0) for status, total in status_rows.all()}

    return AnalyticsOverview(
        total_documents_processed=metric_totals.get(UsageMetricType.document_processed.value, 0),
        total_pages_processed=metric_totals.get(UsageMetricType.page_processed.value, 0),
        total_llm_tokens_input=metric_totals.get(UsageMetricType.llm_tokens_input.value, 0),
        total_llm_tokens_output=metric_totals.get(UsageMetricType.llm_tokens_output.value, 0),
        processing_success_count=status_counts.get(ProcessingJobStatus.completed.value, 0),
        processing_failed_count=status_counts.get(ProcessingJobStatus.failed.value, 0),
    )


async def load_daily_processing_stats(
    db: AsyncSession,
    org_id: UUID,
    *,
    days: int,
) -> list[DailyProcessingStat]:
    day_bucket = func.date_trunc("day", UsageEvent.created_at)
    start_time = datetime.now(UTC) - timedelta(days=days)
    rows = await db.execute(
        select(
            day_bucket.label("day"),
            func.sum(
                case(
                    (
                        UsageEvent.metric_type == UsageMetricType.document_processed,
                        UsageEvent.quantity,
                    ),
                    else_=0,
                )
            ).label("documents_processed"),
            func.sum(
                case(
                    (
                        UsageEvent.metric_type == UsageMetricType.page_processed,
                        UsageEvent.quantity,
                    ),
                    else_=0,
                )
            ).label("pages_processed"),
        )
        .where(UsageEvent.org_id == org_id)
        .where(UsageEvent.created_at >= start_time)
        .group_by(day_bucket)
        .order_by(day_bucket.asc())
    )
    return [
        DailyProcessingStat(
            day=day,
            documents_processed=int(documents_processed or 0),
            pages_processed=int(pages_processed or 0),
        )
        for day, documents_processed, pages_processed in rows.all()
    ]
