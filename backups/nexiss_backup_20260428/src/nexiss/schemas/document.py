"""Pydantic schemas for documents — includes declared_type on upload."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from nexiss.db.models.classification import DocumentCategory
from nexiss.db.models.document import DocumentStatus
from nexiss.db.models.processing_job import ProcessingJobStatus


class DocumentCreateRequest(BaseModel):
    file_name: str = Field(min_length=1, max_length=255)
    content_type: str
    storage_key: str = Field(min_length=1, max_length=1024)
    # User declares the document category on upload (optional but recommended)
    declared_type: DocumentCategory | None = None
    # Optional free-text sub-type hint e.g. "invoice", "prescription"
    declared_subtype: str | None = Field(default=None, max_length=64)


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    org_id: UUID
    created_by_user_id: UUID | None
    file_name: str
    content_type: str
    storage_key: str
    status: DocumentStatus
    page_count: int | None
    extracted_data: dict | None
    confidence_score: Decimal | None
    processing_attempts: int
    last_error: str | None
    declared_type: str | None
    confirmed_type: str | None
    document_subtype: str | None
    type_confidence: Decimal | None
    created_at: datetime
    updated_at: datetime


class DocumentProcessResponse(BaseModel):
    document_id: UUID
    status: DocumentStatus
    task_id: str
    job_id: UUID


class DocumentProgressResponse(BaseModel):
    job_id: UUID
    document_id: UUID
    status: ProcessingJobStatus
    progress_percentage: int
    current_step: str
    error_message: str | None
    task_id: str
    updated_at: datetime


class DocumentSearchResponse(BaseModel):
    """Lightweight search result item."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    file_name: str
    status: DocumentStatus
    confirmed_type: str | None
    document_subtype: str | None
    declared_type: str | None
    page_count: int | None
    created_at: datetime


class EntityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    canonical_name: str
    entity_kind: str
    created_at: datetime
