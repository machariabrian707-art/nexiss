from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4

import pytest

from nexiss.services.analytics.queries import load_analytics_overview, load_daily_processing_stats


class _FakeResult:
    def __init__(self, rows):
        self._rows = rows

    def all(self):
        return self._rows


class _FakeAsyncSession:
    def __init__(self, rows_sequence):
        self.rows_sequence = list(rows_sequence)

    async def execute(self, _stmt):
        return _FakeResult(self.rows_sequence.pop(0))


@pytest.mark.asyncio
async def test_load_analytics_overview_aggregates_metrics_and_statuses() -> None:
    usage_rows = [
        (SimpleNamespace(value="document_processed"), 10),
        (SimpleNamespace(value="page_processed"), 40),
        (SimpleNamespace(value="llm_tokens_input"), 1000),
        (SimpleNamespace(value="llm_tokens_output"), 300),
    ]
    status_rows = [
        (SimpleNamespace(value="completed"), 8),
        (SimpleNamespace(value="failed"), 2),
    ]
    session = _FakeAsyncSession([usage_rows, status_rows])

    overview = await load_analytics_overview(session, uuid4())

    assert overview.total_documents_processed == 10
    assert overview.total_pages_processed == 40
    assert overview.total_llm_tokens_input == 1000
    assert overview.total_llm_tokens_output == 300
    assert overview.processing_success_count == 8
    assert overview.processing_failed_count == 2


@pytest.mark.asyncio
async def test_load_daily_processing_stats_returns_points() -> None:
    now = datetime.now(UTC)
    rows = [(now, 3, 12), (now, 2, 9)]
    session = _FakeAsyncSession([rows])

    stats = await load_daily_processing_stats(session, uuid4(), days=7)

    assert len(stats) == 2
    assert stats[0].documents_processed == 3
    assert stats[0].pages_processed == 12
