"""Document search endpoint — find documents by entity name.

Examples:
  GET /api/v1/search?q=Doshi
  GET /api/v1/search?q=John+Mwangi&doc_type=patient_record
  GET /api/v1/search?q=KRA&doc_type=tax_document
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from nexiss.api.deps.auth import AuthContext, require_org_context
from nexiss.db.session import get_db_session
from nexiss.schemas.document import DocumentResponse
from nexiss.services.entity_service import EntityService

router = APIRouter(prefix="/search", tags=["search"])
_entity_service = EntityService()


@router.get("", response_model=list[DocumentResponse])
async def search_documents(
    q: str = Query(min_length=2, description="Entity name to search for (fuzzy match)"),
    doc_type: str | None = Query(default=None, description="Filter by document type"),
    limit: int = Query(default=50, ge=1, le=200),
    auth: AuthContext = Depends(require_org_context),
    db: AsyncSession = Depends(get_db_session),
) -> list[DocumentResponse]:
    """Search documents by entity name with optional document type filter."""
    docs = await _entity_service.search(
        db=db,
        org_id=auth.active_org_id,
        query=q,
        doc_type=doc_type,
        limit=limit,
    )
    return [DocumentResponse.model_validate(d) for d in docs]
