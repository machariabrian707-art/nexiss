from __future__ import annotations

from types import SimpleNamespace
from uuid import uuid4

from nexiss.db.models.processing_job import ProcessingJobStatus
from nexiss.services.realtime.progress_events import build_progress_event, progress_channel_name


def test_progress_channel_name_is_org_scoped() -> None:
    org_id = uuid4()
    channel = progress_channel_name(org_id)
    assert str(org_id) in channel


def test_build_progress_event_contains_required_fields() -> None:
    job = SimpleNamespace(
        id=uuid4(),
        org_id=uuid4(),
        document_id=uuid4(),
        task_id="task-123",
        status=ProcessingJobStatus.running,
        progress_percentage=50,
        current_step="running_pipeline",
        error_message=None,
    )
    event = build_progress_event(job)

    assert event["event"] == "document_progress"
    assert event["task_id"] == "task-123"
    assert event["status"] == "running"
    assert event["progress_percentage"] == 50
