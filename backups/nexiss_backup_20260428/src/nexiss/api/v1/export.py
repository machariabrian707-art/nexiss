"""Export endpoints: download processed document data as spreadsheet."""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from nexiss.api.deps.auth import AuthContext, require_org_context
from nexiss.db.models.document import Document, DocumentStatus
from nexiss.db.session import get_db_session
from nexiss.services.export.xlsx_export import export_documents_to_xlsx

router = APIRouter(prefix="/export", tags=["export"])


@router.get("/documents.xlsx")
async def export_documents_xlsx(
    auth: AuthContext = Depends(require_org_context),
    db: AsyncSession = Depends(get_db_session),
    doc_type: str | None = Query(default=None, description="Filter by confirmed_type"),
    status_filter: str | None = Query(default=None, alias="status"),
    limit: int = Query(default=1000, ge=1, le=5000),
) -> Response:
    """
    Export completed documents as an Excel spreadsheet.
    Extracted fields become columns automatically.
    Medical records are sorted by patient + date.
    """
    stmt = (
        select(Document)
        .where(
            Document.org_id == auth.active_org_id,
            Document.status == DocumentStatus.completed,
        )
        .order_by(Document.created_at.desc())
        .limit(limit)
    )
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

    rows = await db.execute(stmt)
    documents = list(rows.scalars().all())

    if not documents:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No completed documents found for this filter.",
        )

    try:
        xlsx_bytes = export_documents_to_xlsx(documents)
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    filename = f"nexiss_export_{doc_type or 'all'}.xlsx"
    return Response(
        content=xlsx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
