from __future__ import annotations

from uuid import UUID

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from nexiss.core.config import get_settings
from nexiss.db.models.automation import AutomationTriggerType
from nexiss.db.models.document import Document, DocumentStatus
from nexiss.db.models.processing_job import ProcessingJob, ProcessingJobStatus
from nexiss.db.models.usage_event import UsageEvent, UsageMetricType
from nexiss.services.ai.pipeline import DocumentProcessingPipeline
from nexiss.services.automation.engine import execute_internal_automation
from nexiss.services.realtime.progress_events import publish_progress_event
from nexiss.worker.celery_app import celery_app

settings = get_settings()
sync_engine = create_engine(settings.database_url_sync, pool_pre_ping=True)
SyncSessionFactory = sessionmaker(bind=sync_engine, class_=Session, autoflush=False, expire_on_commit=False)


def _truncate_error_message(message: str, max_length: int = 1024) -> str:
    if len(message) <= max_length:
        return message
    return message[: max_length - 3] + "..."


def _set_job_progress(
    job: ProcessingJob,
    *,
    status: ProcessingJobStatus,
    progress_percentage: int,
    current_step: str,
    error_message: str | None = None,
) -> None:
    job.status = status
    job.progress_percentage = progress_percentage
    job.current_step = current_step
    job.error_message = error_message
    publish_progress_event(job)


@celery_app.task(name="nexiss.documents.process_document")
def process_document_task(document_id: str, job_id: str) -> dict[str, str]:
    with SyncSessionFactory() as db:
        target_id = UUID(document_id)
        row = db.execute(select(Document).where(Document.id == target_id))
        document = row.scalar_one_or_none()
        if document is None:
            raise ValueError("Document not found")
        job_result = db.execute(select(ProcessingJob).where(ProcessingJob.id == UUID(job_id)))
        job = job_result.scalar_one_or_none()
        if job is None:
            raise ValueError("Processing job not found")

        try:
            document.processing_attempts += 1
            document.status = DocumentStatus.processing
            document.last_error = None
            _set_job_progress(
                job,
                status=ProcessingJobStatus.running,
                progress_percentage=10,
                current_step="starting",
            )
            db.flush()

            pipeline = DocumentProcessingPipeline()
            _set_job_progress(
                job,
                status=ProcessingJobStatus.running,
                progress_percentage=50,
                current_step="running_pipeline",
            )
            pipeline_result = pipeline.run(document)

            document.page_count = pipeline_result.page_count
            document.extracted_data = pipeline_result.extracted_data
            document.confidence_score = pipeline_result.confidence_score
            document.status = DocumentStatus.completed
            _set_job_progress(
                job,
                status=ProcessingJobStatus.completed,
                progress_percentage=100,
                current_step="completed",
            )

            db.add(
                UsageEvent(
                    org_id=document.org_id,
                    document_id=document.id,
                    metric_type=UsageMetricType.document_processed,
                    quantity=1,
                    details={"pipeline": "ocr_llm_v1"},
                )
            )
            db.add(
                UsageEvent(
                    org_id=document.org_id,
                    document_id=document.id,
                    metric_type=UsageMetricType.page_processed,
                    quantity=document.page_count,
                    details={"pipeline": "ocr_llm_v1"},
                )
            )
            db.add(
                UsageEvent(
                    org_id=document.org_id,
                    document_id=document.id,
                    metric_type=UsageMetricType.llm_tokens_input,
                    quantity=pipeline_result.tokens_input,
                    details={"pipeline": "ocr_llm_v1", "model": settings.llm_model},
                )
            )
            db.add(
                UsageEvent(
                    org_id=document.org_id,
                    document_id=document.id,
                    metric_type=UsageMetricType.llm_tokens_output,
                    quantity=pipeline_result.tokens_output,
                    details={"pipeline": "ocr_llm_v1", "model": settings.llm_model},
                )
            )
            execute_internal_automation(
                db,
                document=document,
                trigger_type=AutomationTriggerType.document_processed,
            )
            db.commit()
        except Exception as exc:
            document.status = DocumentStatus.failed
            document.last_error = _truncate_error_message(str(exc))
            _set_job_progress(
                job,
                status=ProcessingJobStatus.failed,
                progress_percentage=100,
                current_step="failed",
                error_message=document.last_error,
            )
            db.commit()
            raise

    return {"document_id": document_id, "status": DocumentStatus.completed.value, "job_id": job_id}
