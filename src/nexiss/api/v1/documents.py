"""Documents API — full CRUD + search + entity endpoints."""
from __future__ import annotations

from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from nexiss.api.deps.auth import AuthContext, require_org_admin, require_org_context
from nexiss.db.models.document import Document, DocumentStatus
from nexiss.db.models.entity import DocumentEntity, Entity
from nexiss.db.models.processing_job import ProcessingJob, ProcessingJobStatus
from nexiss.db.session import get_db_session
from nexiss.schemas.document import (
    DocumentCreateRequest,
    DocumentProcessResponse,
    DocumentProgressResponse,
    DocumentResponse,
    DocumentSearchResponse,
    EntityResponse,
)
from nexiss.services.storage.s3_service import validate_content_type
from nexiss.worker.tasks import process_document_task

router = APIRouter(prefix="/documents", tags=["documents"])


def _assert_org_storage_key(storage_key: str, org_id: UUID) -> None:
    if not storage_key.startswith(f"{org_id}/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="storage_key must be namespaced under the active organization",
        )


async def _queue_processing_job(db: AsyncSession, document: Document) -> ProcessingJob:
    job = ProcessingJob(
        org_id=document.org_id,
        document_id=document.id,
        task_id=str(uuid4()),
        status=ProcessingJobStatus.queued,
        progress_percentage=0,
        current_step="queued",
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)
    process_document_task.apply_async(args=[str(document.id), str(job.id)], task_id=job.task_id)
    return job


# ---------------------------------------------------------------------------
# CREATE
# ---------------------------------------------------------------------------
@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(
    payload: DocumentCreateRequest,
    auth: AuthContext = Depends(require_org_admin),
    db: AsyncSession = Depends(get_db_session),
) -> DocumentResponse:
    try:
        validate_content_type(payload.content_type)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    _assert_org_storage_key(payload.storage_key, auth.active_org_id)

    existing = await db.execute(
        select(Document).where(
            Document.org_id == auth.active_org_id,
            Document.storage_key == payload.storage_key,
        )
    )
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Document already exists")

    document = Document(
        org_id=auth.active_org_id,
        created_by_user_id=auth.user.id,
        file_name=payload.file_name,
        content_type=payload.content_type,
        storage_key=payload.storage_key,
        status=DocumentStatus.uploaded,
        declared_type=payload.declared_type.value if payload.declared_type else None,
        document_subtype=payload.declared_subtype,
    )
    db.add(document)
    await db.commit()
    await db.refresh(document)
    return DocumentResponse.model_validate(document)


# ---------------------------------------------------------------------------
# LIST
# ---------------------------------------------------------------------------
@router.get("", response_model=list[DocumentResponse])
async def list_documents(
    auth: AuthContext = Depends(require_org_context),
    db: AsyncSession = Depends(get_db_session),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> list[DocumentResponse]:
    rows = await db.execute(
        select(Document)
        .where(Document.org_id == auth.active_org_id)
        .order_by(Document.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return [DocumentResponse.model_validate(d) for d in rows.scalars().all()]


# ---------------------------------------------------------------------------
# SEARCH  —  "show all invoices from Doshi"
# ---------------------------------------------------------------------------
@router.get("/search", response_model=list[DocumentSearchResponse])
async def search_documents(
    auth: AuthContext = Depends(require_org_context),
    db: AsyncSession = Depends(get_db_session),
    q: str | None = Query(default=None, description="Free-text search on file_name"),
    doc_type: str | None = Query(default=None, description="Filter by confirmed_type or declared_type"),
    entity_name: str | None = Query(
        default=None,
        description="Filter documents linked to this entity (fuzzy matched to canonical_name)",
    ),
    status_filter: str | None = Query(default=None, alias="status"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> list[DocumentSearchResponse]:
    stmt = select(Document).where(Document.org_id == auth.active_org_id)

    if q:
        stmt = stmt.where(Document.file_name.ilike(f"%{q}%"))

    if doc_type:
        stmt = stmt.where(
            (Document.confirmed_type == doc_type) | (Document.declared_type == doc_type)
        )

    if status_filter:
        try:
            s = DocumentStatus(status_filter)
            stmt = stmt.where(Document.status == s)
        except ValueError:
            pass

    if entity_name:
        # Find entity by fuzzy canonical name match then join
        norm = " ".join(entity_name.lower().split())
        entity_rows = await db.execute(
            select(Entity).where(
                Entity.org_id == auth.active_org_id,
                Entity.canonical_name.ilike(f"%{norm}%"),
            )
        )
        entity_ids = [e.id for e in entity_rows.scalars().all()]
        if not entity_ids:
            return []
        doc_ids_rows = await db.execute(
            select(DocumentEntity.document_id).where(
                DocumentEntity.entity_id.in_(entity_ids),
                DocumentEntity.org_id == auth.active_org_id,
            )
        )
        doc_ids = [r for r in doc_ids_rows.scalars().all()]
        if not doc_ids:
            return []
        stmt = stmt.where(Document.id.in_(doc_ids))

    stmt = stmt.order_by(Document.created_at.desc()).limit(limit).offset(offset)
    rows = await db.execute(stmt)
    return [DocumentSearchResponse.model_validate(d) for d in rows.scalars().all()]


# ---------------------------------------------------------------------------
# GET ONE
# ---------------------------------------------------------------------------
@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: UUID,
    auth: AuthContext = Depends(require_org_context),
    db: AsyncSession = Depends(get_db_session),
) -> DocumentResponse:
    row = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.org_id == auth.active_org_id,
        )
    )
    document = row.scalar_one_or_none()
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return DocumentResponse.model_validate(document)


# ---------------------------------------------------------------------------
# ENTITIES linked to a document
# ---------------------------------------------------------------------------
@router.get("/{document_id}/entities", response_model=list[EntityResponse])
async def get_document_entities(
    document_id: UUID,
    auth: AuthContext = Depends(require_org_context),
    db: AsyncSession = Depends(get_db_session),
) -> list[EntityResponse]:
    rows = await db.execute(
        select(Entity)
        .join(DocumentEntity, DocumentEntity.entity_id == Entity.id)
        .where(
            DocumentEntity.document_id == document_id,
            DocumentEntity.org_id == auth.active_org_id,
        )
    )
    return [EntityResponse.model_validate(e) for e in rows.scalars().all()]


# ---------------------------------------------------------------------------
# PROCESS / RETRY / PROGRESS (unchanged structure, updated to pass new fields)
# ---------------------------------------------------------------------------
@router.post("/{document_id}/process", response_model=DocumentProcessResponse)
async def process_document(
    document_id: UUID,
    auth: AuthContext = Depends(require_org_admin),
    db: AsyncSession = Depends(get_db_session),
) -> DocumentProcessResponse:
    row = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.org_id == auth.active_org_id,
        )
    )
    document = row.scalar_one_or_none()
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    if document.status == DocumentStatus.processing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Document is already being processed",
        )
    document.status = DocumentStatus.processing
    document.last_error = None
    job = await _queue_processing_job(db, document)
    return DocumentProcessResponse(
        document_id=document.id, status=document.status, task_id=job.task_id, job_id=job.id
    )


@router.post("/{document_id}/retry", response_model=DocumentProcessResponse)
async def retry_document_processing(
    document_id: UUID,
    auth: AuthContext = Depends(require_org_admin),
    db: AsyncSession = Depends(get_db_session),
) -> DocumentProcessResponse:
    row = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.org_id == auth.active_org_id,
        )
    )
    document = row.scalar_one_or_none()
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    if document.status != DocumentStatus.failed:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Retry is allowed only for failed documents",
        )
    document.status = DocumentStatus.processing
    document.last_error = None
    job = await _queue_processing_job(db, document)
    return DocumentProcessResponse(
        document_id=document.id, status=document.status, task_id=job.task_id, job_id=job.id
    )


@router.get("/{document_id}/progress", response_model=DocumentProgressResponse)
async def get_document_progress(
    document_id: UUID,
    auth: AuthContext = Depends(require_org_context),
    db: AsyncSession = Depends(get_db_session),
) -> DocumentProgressResponse:
    result = await db.execute(
        select(ProcessingJob)
        .where(
            ProcessingJob.document_id == document_id,
            ProcessingJob.org_id == auth.active_org_id,
        )
        .order_by(ProcessingJob.created_at.desc())
        .limit(1)
    )
    job = result.scalar_one_or_none()
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No processing job found")
    return DocumentProgressResponse(
        job_id=job.id,
        document_id=job.document_id,
        status=job.status,
        progress_percentage=job.progress_percentage,
        current_step=job.current_step,
        error_message=job.error_message,
        task_id=job.task_id,
        updated_at=job.updated_at,
    )
