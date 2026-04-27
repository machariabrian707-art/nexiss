from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AnalyticsOverviewResponse(BaseModel):
    org_id: UUID
    total_documents_processed: int
    total_pages_processed: int
    total_llm_tokens_input: int
    total_llm_tokens_output: int
    processing_success_count: int
    processing_failed_count: int


class DailyProcessingPoint(BaseModel):
    day: datetime
    documents_processed: int
    pages_processed: int


class AnalyticsDailyProcessingResponse(BaseModel):
    org_id: UUID
    points: list[DailyProcessingPoint]
