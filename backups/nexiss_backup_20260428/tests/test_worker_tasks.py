from __future__ import annotations

from types import SimpleNamespace
from uuid import uuid4

from nexiss.db.models.document import DocumentStatus
from nexiss.db.models.processing_job import ProcessingJobStatus
from nexiss.db.models.usage_event import UsageMetricType
from nexiss.worker import tasks


def test_process_document_task_marks_document_completed(monkeypatch) -> None:
    document_id = uuid4()
    job_id = uuid4()
    fake_document = SimpleNamespace(
        id=document_id,
        org_id=uuid4(),
        file_name="invoice.pdf",
        content_type="application/pdf",
        page_count=None,
        extracted_data=None,
        confidence_score=None,
        processing_attempts=0,
        last_error=None,
        status=DocumentStatus.uploaded,
    )
    fake_job = SimpleNamespace(
        id=job_id,
        status=ProcessingJobStatus.queued,
        progress_percentage=0,
        current_step="queued",
        error_message=None,
    )

    class FakeResult:
        def __init__(self, value):
            self._value = value

        def scalar_one_or_none(self):
            return self._value

    class FakeSession:
        def __init__(self) -> None:
            self.added: list[object] = []

        def execute(self, _stmt):
            stmt_text = str(_stmt)
            if "processing_jobs" in stmt_text:
                return FakeResult(fake_job)
            return FakeResult(fake_document)

        def flush(self) -> None:
            return None

        def add(self, value: object) -> None:
            self.added.append(value)

        def commit(self) -> None:
            return None

    class FakeSessionFactory:
        def __init__(self):
            self.session = FakeSession()

        def __call__(self):
            return self

        def __enter__(self):
            return self.session

        def __exit__(self, exc_type, exc, tb):
            return False

    session_factory = FakeSessionFactory()
    monkeypatch.setattr(tasks, "SyncSessionFactory", session_factory)
    monkeypatch.setattr(tasks, "publish_progress_event", lambda _job: None)
    monkeypatch.setattr(
        tasks,
        "execute_internal_automation",
        lambda *_args, **_kwargs: SimpleNamespace(runs_created=0, succeeded=0, failed=0),
    )
    monkeypatch.setattr(
        tasks,
        "DocumentProcessingPipeline",
        lambda: SimpleNamespace(
            run=lambda _doc: SimpleNamespace(
                page_count=2,
                extracted_data={"vendor": "Acme"},
                confidence_score=0.91,
                tokens_input=123,
                tokens_output=41,
            )
        ),
    )

    result = tasks.process_document_task(str(document_id), str(job_id))

    assert result == {
        "document_id": str(document_id),
        "status": DocumentStatus.completed.value,
        "job_id": str(job_id),
    }
    assert fake_document.status == DocumentStatus.completed
    assert fake_document.page_count == 2
    assert fake_document.processing_attempts == 1
    assert fake_document.last_error is None
    assert len(session_factory.session.added) == 4
    metric_types = {getattr(item, "metric_type", None) for item in session_factory.session.added}
    assert metric_types == {
        UsageMetricType.document_processed,
        UsageMetricType.page_processed,
        UsageMetricType.llm_tokens_input,
        UsageMetricType.llm_tokens_output,
    }
    assert fake_job.status == ProcessingJobStatus.completed
    assert fake_job.progress_percentage == 100
    assert fake_job.current_step == "completed"


def test_truncate_error_message_caps_length() -> None:
    message = "x" * 2000
    truncated = tasks._truncate_error_message(message, max_length=32)

    assert len(truncated) == 32
    assert truncated.endswith("...")
