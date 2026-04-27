"""Celery task: process a single document through the full pipeline.

Enhanced to:
  - Persist confirmed_type, document_subtype, type_confidence after classification.
  - Run entity matching + link entities to document inside the same transaction.
"""
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
SyncSessionFactory = sessionmaker(
    bind=sync_engine, class_=Session, autoflush=False, expire_on_commit=False
)


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


def _resolve_entities_sync(
    db: Session,
    org_id: UUID,
    document_id: UUID,
    entities: list[dict],
) -> None:
    """Synchronous entity resolution used inside the Celery worker."""
    from nexiss.db.models.entity import DocumentEntity, Entity, EntityAlias
    import difflib

    FUZZY_THRESHOLD = 0.82
    REVIEW_PREFIX = "review:"

    def _norm(name: str) -> str:
        return " ".join(name.lower().split())

    def _score(a: str, b: str) -> float:
        return difflib.SequenceMatcher(None, _norm(a), _norm(b)).ratio()

    for ent_dict in entities:
        raw_name: str = ent_dict.get("name", "").strip()
        entity_kind: str = ent_dict.get("kind", "unknown")
        if not raw_name:
            continue
        norm = _norm(raw_name)

        # Exact canonical
        row = db.execute(
            select(Entity).where(Entity.org_id == org_id, Entity.canonical_name == norm)
        ).scalar_one_or_none()
        if row:
            entity_id = row.id
        else:
            # Exact alias
            alias_row = db.execute(
                select(EntityAlias)
                .join(Entity, EntityAlias.entity_id == Entity.id)
                .where(Entity.org_id == org_id, EntityAlias.alias == norm)
            ).scalar_one_or_none()
            if alias_row:
                entity_id = alias_row.entity_id
            else:
                # Fuzzy scan
                all_ents = db.execute(
                    select(Entity).where(Entity.org_id == org_id)
                ).scalars().all()
                best_score = 0.0
                best_ent = None
                for e in all_ents:
                    s = _score(raw_name, e.canonical_name)
                    if s > best_score:
                        best_score, best_ent = s, e

                if best_ent and best_score >= FUZZY_THRESHOLD:
                    entity_id = best_ent.id
                    db.add(EntityAlias(entity_id=entity_id, alias=norm))
                    db.flush()
                else:
                    new_ent = Entity(org_id=org_id, canonical_name=norm, entity_kind=entity_kind)
                    db.add(new_ent)
                    db.flush()
                    entity_id = new_ent.id
                    if best_ent and best_score >= 0.60:
                        db.add(EntityAlias(
                            entity_id=entity_id,
                            alias=f"{REVIEW_PREFIX}{best_ent.id}",
                        ))
                        db.flush()

        # Link to document (idempotent)
        existing = db.execute(
            select(DocumentEntity).where(
                DocumentEntity.document_id == document_id,
                DocumentEntity.entity_id == entity_id,
            )
        ).scalar_one_or_none()
        if existing is None:
            db.add(DocumentEntity(
                org_id=org_id,
                document_id=document_id,
                entity_id=entity_id,
                role=entity_kind,
            ))
            db.flush()


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
                progress_percentage=40,
                current_step="ocr_and_extraction",
            )
            pipeline_result = pipeline.run(document)

            _set_job_progress(
                job,
                status=ProcessingJobStatus.running,
                progress_percentage=70,
                current_step="classifying_and_linking_entities",
            )

            # Persist classification
            document.confirmed_type = pipeline_result.confirmed_type
            document.document_subtype = pipeline_result.document_subtype
            document.type_confidence = pipeline_result.type_confidence
            document.page_count = pipeline_result.page_count
            document.extracted_data = pipeline_result.extracted_data
            document.confidence_score = pipeline_result.confidence_score
            document.status = DocumentStatus.completed

            # Entity matching
            _resolve_entities_sync(
                db,
                org_id=document.org_id,
                document_id=document.id,
                entities=pipeline_result.entities,
            )

            _set_job_progress(
                job,
                status=ProcessingJobStatus.completed,
                progress_percentage=100,
                current_step="completed",
            )

            db.add(UsageEvent(
                org_id=document.org_id,
                document_id=document.id,
                metric_type=UsageMetricType.document_processed,
                quantity=1,
                details={"pipeline": "ocr_llm_v2", "type": document.confirmed_type},
            ))
            db.add(UsageEvent(
                org_id=document.org_id,
                document_id=document.id,
                metric_type=UsageMetricType.page_processed,
                quantity=document.page_count,
                details={"pipeline": "ocr_llm_v2"},
            ))
            db.add(UsageEvent(
                org_id=document.org_id,
                document_id=document.id,
                metric_type=UsageMetricType.llm_tokens_input,
                quantity=pipeline_result.tokens_input,
                details={"pipeline": "ocr_llm_v2", "model": settings.llm_model},
            ))
            db.add(UsageEvent(
                org_id=document.org_id,
                document_id=document.id,
                metric_type=UsageMetricType.llm_tokens_output,
                quantity=pipeline_result.tokens_output,
                details={"pipeline": "ocr_llm_v2", "model": settings.llm_model},
            ))
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
