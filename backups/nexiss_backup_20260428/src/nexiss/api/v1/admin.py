"""Super Admin API — platform-owner oversight.

Access is gated by `is_superuser` on the User model (existing field).
"""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from nexiss.api.deps import get_current_user
from nexiss.db.models.document import Document, DocumentStatus
from nexiss.db.models.entity import Entity, EntityAlias
from nexiss.db.models.org_membership import OrgMembership
from nexiss.db.models.organization import Organization
from nexiss.db.models.user import User
from nexiss.db.session import get_db_session
from pydantic import BaseModel, ConfigDict

router = APIRouter(prefix="/admin", tags=["super-admin"])


async def require_superadmin(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super-admin access required",
        )
    return current_user


class OrgSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    org_id: UUID
    name: str
    created_at: datetime
    member_count: int
    document_count: int


class PlatformStats(BaseModel):
    total_orgs: int
    total_users: int
    total_documents: int
    documents_completed: int
    documents_failed: int
    documents_processing: int


class AdminDocumentRow(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    org_id: UUID
    file_name: str
    status: DocumentStatus
    confirmed_type: str | None
    declared_type: str | None
    page_count: int | None
    created_at: datetime


class EntityReviewItem(BaseModel):
    entity_id: UUID
    org_id: UUID
    canonical_name: str
    entity_kind: str
    candidate_match_id: str
    created_at: datetime


@router.get("/stats", response_model=PlatformStats)
async def platform_stats(
    _: User = Depends(require_superadmin),
    db: AsyncSession = Depends(get_db_session),
) -> PlatformStats:
    total_orgs = (await db.execute(select(func.count(Organization.org_id)))).scalar_one()
    total_users = (await db.execute(select(func.count(User.id)))).scalar_one()
    total_docs = (await db.execute(select(func.count(Document.id)))).scalar_one()
    status_rows = await db.execute(
        select(Document.status, func.count(Document.id)).group_by(Document.status)
    )
    status_counts = {s.value: c for s, c in status_rows.all()}
    return PlatformStats(
        total_orgs=total_orgs,
        total_users=total_users,
        total_documents=total_docs,
        documents_completed=status_counts.get(DocumentStatus.completed.value, 0),
        documents_failed=status_counts.get(DocumentStatus.failed.value, 0),
        documents_processing=status_counts.get(DocumentStatus.processing.value, 0),
    )


@router.get("/orgs", response_model=list[OrgSummary])
async def list_all_orgs(
    _: User = Depends(require_superadmin),
    db: AsyncSession = Depends(get_db_session),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> list[OrgSummary]:
    orgs = (await db.execute(
        select(Organization).order_by(Organization.created_at.desc()).limit(limit).offset(offset)
    )).scalars().all()
    result = []
    for org in orgs:
        member_count = (await db.execute(
            select(func.count(OrgMembership.user_id)).where(OrgMembership.org_id == org.org_id)
        )).scalar_one()
        doc_count = (await db.execute(
            select(func.count(Document.id)).where(Document.org_id == org.org_id)
        )).scalar_one()
        result.append(OrgSummary(
            org_id=org.org_id,
            name=org.name,
            created_at=org.created_at,
            member_count=member_count,
            document_count=doc_count,
        ))
    return result


@router.get("/documents", response_model=list[AdminDocumentRow])
async def list_all_documents(
    _: User = Depends(require_superadmin),
    db: AsyncSession = Depends(get_db_session),
    org_id: UUID | None = Query(default=None),
    doc_type: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> list[AdminDocumentRow]:
    stmt = select(Document).order_by(Document.created_at.desc()).limit(limit).offset(offset)
    if org_id:
        stmt = stmt.where(Document.org_id == org_id)
    if doc_type:
        stmt = stmt.where(
            (Document.confirmed_type == doc_type) | (Document.declared_type == doc_type)
        )
    rows = (await db.execute(stmt)).scalars().all()
    return [AdminDocumentRow.model_validate(d) for d in rows]


@router.get("/entity-review", response_model=list[EntityReviewItem])
async def entity_review_queue(
    _: User = Depends(require_superadmin),
    db: AsyncSession = Depends(get_db_session),
    limit: int = Query(default=100, ge=1, le=500),
) -> list[EntityReviewItem]:
    review_aliases = (await db.execute(
        select(EntityAlias)
        .where(EntityAlias.alias.startswith("review:"))
        .limit(limit)
    )).scalars().all()
    result = []
    for alias in review_aliases:
        entity = await db.get(Entity, alias.entity_id)
        if entity:
            result.append(EntityReviewItem(
                entity_id=entity.id,
                org_id=entity.org_id,
                canonical_name=entity.canonical_name,
                entity_kind=entity.entity_kind,
                candidate_match_id=alias.alias.removeprefix("review:"),
                created_at=entity.created_at,
            ))
    return result


@router.post("/entity-review/{entity_id}/merge")
async def merge_entity(
    entity_id: UUID,
    target_id: UUID = Query(description="Entity to merge INTO"),
    _: User = Depends(require_superadmin),
    db: AsyncSession = Depends(get_db_session),
) -> dict:
    from nexiss.db.models.entity import DocumentEntity
    from sqlalchemy import delete, update

    await db.execute(
        update(DocumentEntity)
        .where(DocumentEntity.entity_id == entity_id)
        .values(entity_id=target_id)
    )
    await db.execute(delete(EntityAlias).where(EntityAlias.entity_id == entity_id))
    await db.execute(delete(Entity).where(Entity.id == entity_id))
    await db.commit()
    return {"merged": str(entity_id), "into": str(target_id)}
