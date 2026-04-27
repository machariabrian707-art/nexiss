"""Super Admin API — platform owner (you) can see everything.

Protected by a separate admin role check: only users with role=admin
in any org membership AND the special NEXISS_ADMIN_SECRET header.

Endpoints:
  GET  /admin/stats          - platform-wide overview
  GET  /admin/orgs           - all organisations
  GET  /admin/orgs/{org_id}/documents - all docs for an org
  GET  /admin/users          - all users
  GET  /admin/documents      - all documents across all orgs
  GET  /admin/documents/{id} - single document (any org)
"""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from nexiss.api.deps.auth import AuthContext, require_org_context
from nexiss.core.config import get_settings
from nexiss.db.models.document import Document, DocumentStatus
from nexiss.db.models.organization import Organization
from nexiss.db.models.usage_event import UsageEvent
from nexiss.db.models.user import User
from nexiss.db.session import get_db_session
from nexiss.schemas.document import DocumentResponse

router = APIRouter(prefix="/admin", tags=["admin"])
settings = get_settings()


# ---------------------------------------------------------------------------
# Admin guard — must send the secret header
# ---------------------------------------------------------------------------

async def require_admin_secret(
    x_admin_secret: str | None = Header(default=None, alias="X-Admin-Secret"),
) -> None:
    expected = settings.nexiss_admin_secret
    if not expected or x_admin_secret != expected:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access denied",
        )


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class PlatformStats(BaseModel):
    total_orgs: int
    total_users: int
    total_documents: int
    documents_completed: int
    documents_failed: int
    documents_processing: int
    total_pages_processed: int


class OrgSummary(BaseModel):
    org_id: UUID
    name: str
    slug: str
    created_at: str


class UserSummary(BaseModel):
    id: UUID
    email: str
    full_name: str | None
    is_active: bool
    created_at: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/stats", response_model=PlatformStats, dependencies=[Depends(require_admin_secret)])
async def get_platform_stats(
    db: AsyncSession = Depends(get_db_session),
) -> PlatformStats:
    """Platform-wide metrics — the admin dashboard overview."""
    total_orgs = (await db.execute(select(func.count()).select_from(Organization))).scalar_one()
    total_users = (await db.execute(select(func.count()).select_from(User))).scalar_one()
    total_docs = (await db.execute(select(func.count()).select_from(Document))).scalar_one()

    completed = (await db.execute(
        select(func.count()).select_from(Document).where(Document.status == DocumentStatus.completed)
    )).scalar_one()
    failed = (await db.execute(
        select(func.count()).select_from(Document).where(Document.status == DocumentStatus.failed)
    )).scalar_one()
    processing = (await db.execute(
        select(func.count()).select_from(Document).where(Document.status == DocumentStatus.processing)
    )).scalar_one()
    pages = (await db.execute(
        select(func.coalesce(func.sum(Document.page_count), 0)).select_from(Document)
    )).scalar_one()

    return PlatformStats(
        total_orgs=total_orgs,
        total_users=total_users,
        total_documents=total_docs,
        documents_completed=completed,
        documents_failed=failed,
        documents_processing=processing,
        total_pages_processed=int(pages),
    )


@router.get("/orgs", response_model=list[OrgSummary], dependencies=[Depends(require_admin_secret)])
async def list_all_orgs(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db_session),
) -> list[OrgSummary]:
    result = await db.execute(
        select(Organization).order_by(Organization.created_at.desc()).limit(limit).offset(offset)
    )
    orgs = result.scalars().all()
    return [
        OrgSummary(
            org_id=o.org_id,
            name=o.name,
            slug=o.slug,
            created_at=o.created_at.isoformat(),
        )
        for o in orgs
    ]


@router.get("/orgs/{org_id}/documents", response_model=list[DocumentResponse], dependencies=[Depends(require_admin_secret)])
async def list_org_documents(
    org_id: UUID,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    doc_type: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db_session),
) -> list[DocumentResponse]:
    q = select(Document).where(Document.org_id == org_id)
    if doc_type:
        q = q.where(Document.confirmed_type == doc_type)
    q = q.order_by(Document.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(q)
    return [DocumentResponse.model_validate(d) for d in result.scalars().all()]


@router.get("/users", response_model=list[UserSummary], dependencies=[Depends(require_admin_secret)])
async def list_all_users(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db_session),
) -> list[UserSummary]:
    result = await db.execute(
        select(User).order_by(User.created_at.desc()).limit(limit).offset(offset)
    )
    return [
        UserSummary(
            id=u.id,
            email=u.email,
            full_name=u.full_name,
            is_active=u.is_active,
            created_at=u.created_at.isoformat(),
        )
        for u in result.scalars().all()
    ]


@router.get("/documents", response_model=list[DocumentResponse], dependencies=[Depends(require_admin_secret)])
async def list_all_documents(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    doc_type: str | None = Query(default=None),
    status: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db_session),
) -> list[DocumentResponse]:
    q = select(Document)
    if doc_type:
        q = q.where(Document.confirmed_type == doc_type)
    if status:
        q = q.where(Document.status == status)
    q = q.order_by(Document.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(q)
    return [DocumentResponse.model_validate(d) for d in result.scalars().all()]


@router.get("/documents/{document_id}", response_model=DocumentResponse, dependencies=[Depends(require_admin_secret)])
async def get_any_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db_session),
) -> DocumentResponse:
    result = await db.execute(select(Document).where(Document.id == document_id))
    document = result.scalar_one_or_none()
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return DocumentResponse.model_validate(document)
