from datetime import datetime
from typing import Optional, Any
from uuid import UUID
from pydantic import BaseModel, EmailStr


# ── Auth ─────────────────────────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    org_name: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: UUID
    email: str
    full_name: str
    is_superadmin: bool
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class SwitchOrgRequest(BaseModel):
    org_id: UUID


# ── Organisation ─────────────────────────────────────────────────────────────
class OrgOut(BaseModel):
    id: UUID
    name: str
    slug: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ── Document ──────────────────────────────────────────────────────────────────
class DocumentCreate(BaseModel):
    s3_key: str
    filename: str
    doc_type_hint: Optional[str] = None
    content_type: Optional[str] = None
    file_size: Optional[int] = None


class DocumentOut(BaseModel):
    id: UUID
    org_id: UUID
    filename: str
    s3_key: str
    doc_type: Optional[str]
    doc_type_hint: Optional[str]
    status: str
    page_count: Optional[int]
    ocr_text: Optional[str]
    extraction_result: Optional[Any]
    confidence_score: Optional[float]
    needs_review: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentProgressOut(BaseModel):
    job_id: Optional[UUID]
    status: str
    step: Optional[str]
    progress_pct: int
    error: Optional[str]


# ── Storage ───────────────────────────────────────────────────────────────────
class SignedUploadRequest(BaseModel):
    filename: str
    content_type: str


class SignedUploadResponse(BaseModel):
    upload_url: str
    s3_key: str


class SignedDownloadRequest(BaseModel):
    s3_key: str


class SignedDownloadResponse(BaseModel):
    download_url: str


# ── Analytics ─────────────────────────────────────────────────────────────────
class AnalyticsOverview(BaseModel):
    total_documents: int
    completed: int
    failed: int
    processing: int
    uploaded: int
    total_pages: int
    total_llm_tokens: int


class DailyProcessing(BaseModel):
    date: str
    documents: int
    pages: int


# ── Admin ─────────────────────────────────────────────────────────────────────
class AdminStats(BaseModel):
    total_orgs: int
    total_users: int
    total_documents: int
    documents_today: int
    failed_documents: int
    processing_queue: int


class AdminOrgOut(BaseModel):
    id: UUID
    name: str
    slug: str
    created_at: datetime
    member_count: int = 0
    document_count: int = 0

    class Config:
        from_attributes = True


class AdminUserOut(BaseModel):
    id: UUID
    full_name: str
    email: str
    is_superadmin: bool
    is_active: bool
    created_at: datetime
    org_name: Optional[str] = None

    class Config:
        from_attributes = True


class AdminDocumentOut(BaseModel):
    id: UUID
    filename: str
    doc_type: Optional[str]
    status: str
    page_count: Optional[int]
    created_at: datetime
    org_name: Optional[str] = None

    class Config:
        from_attributes = True


# ── Entity ────────────────────────────────────────────────────────────────────
class EntityOut(BaseModel):
    id: UUID
    canonical_name: str
    entity_type: Optional[str]
    aliases: list
    created_at: datetime

    class Config:
        from_attributes = True


# ── Usage ─────────────────────────────────────────────────────────────────────
class UsageSummaryItem(BaseModel):
    metric_type: str
    total: float


# ── Search ────────────────────────────────────────────────────────────────────
class SearchResult(BaseModel):
    id: UUID
    filename: str
    doc_type: Optional[str]
    status: str
    created_at: datetime
    snippet: Optional[str] = None

    class Config:
        from_attributes = True
