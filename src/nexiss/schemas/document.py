from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from nexiss.db.models.document import DocumentStatus
from nexiss.db.models.processing_job import ProcessingJobStatus


class DocumentCreateRequest(BaseModel):
    file_name: str = Field(min_length=1, max_length=255)
    content_type: str
    storage_key: str = Field(min_length=1, max_length=1024)


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
    processing_attempts: int
    last_error: str | None
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
