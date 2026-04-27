"""Export endpoint — download documents as CSV or XLSX spreadsheet.

This is the core Nexiss product promise: messy scanned docs -> clean spreadsheet.

Examples:
  POST /api/v1/export  {"format": "xlsx", "doc_type": "invoice"}
  POST /api/v1/export  {"format": "csv",  "doc_type": "patient_record"}
  POST /api/v1/export  {"format": "xlsx"}  # all document types
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from nexiss.api.deps.auth import AuthContext, require_org_context
from nexiss.db.models.document import Document, DocumentStatus
from nexiss.db.session import get_db_session
from nexiss.services.export_service import export_csv, export_xlsx

router = APIRouter(prefix="/export", tags=["export"])


@router.get("")
async def export_documents(
    format: str = Query(default="csv", pattern="^(csv|xlsx)$"),
    doc_type: str | None = Query(default=None, description="Filter by confirmed_type"),
    limit: int = Query(default=1000, ge=1, le=5000),
    auth: AuthContext = Depends(require_org_context),
    db: AsyncSession = Depends(get_db_session),
) -> Response:
    """Export completed documents to CSV or XLSX."""
    q = select(Document).where(
        Document.org_id == auth.active_org_id,
        Document.status == DocumentStatus.completed,
    )
    if doc_type:
        q = q.where(Document.confirmed_type == doc_type)
    q = q.order_by(Document.created_at.desc()).limit(limit)

    result = await db.execute(q)
    documents = list(result.scalars().all())

    if format == "xlsx":
        content = export_xlsx(documents)
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        filename = f"nexiss_export_{doc_type or 'all'}.xlsx"
    else:
        content = export_csv(documents)
        media_type = "text/csv"
        filename = f"nexiss_export_{doc_type or 'all'}.csv"

    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
