from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.concurrency import run_in_threadpool
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from nexiss.api.deps.auth import AuthContext, require_org_admin, require_org_context
from nexiss.core.config import get_settings
from nexiss.db.models.document import Document
from nexiss.db.session import get_db_session
from nexiss.schemas.storage import (
    SignedDownloadRequest,
    SignedDownloadResponse,
    SignedUploadRequest,
    SignedUploadResponse,
)
from nexiss.services.storage.s3_service import (
    build_storage_key,
    create_download_url,
    create_upload_url,
    validate_content_type,
)

router = APIRouter(prefix="/storage", tags=["storage"])
settings = get_settings()


@router.post("/signed-upload", response_model=SignedUploadResponse)
async def create_signed_upload_url(
    payload: SignedUploadRequest,
    auth: AuthContext = Depends(require_org_admin),
) -> SignedUploadResponse:
    try:
        validate_content_type(payload.content_type)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    storage_key = build_storage_key(auth.active_org_id, payload.file_name)
    upload_url = await run_in_threadpool(create_upload_url, storage_key, payload.content_type)
    return SignedUploadResponse(
        storage_key=storage_key,
        upload_url=upload_url,
        expires_in_seconds=settings.s3_presign_expiry_seconds,
        required_headers={"Content-Type": payload.content_type},
    )


@router.post("/signed-download", response_model=SignedDownloadResponse)
async def create_signed_download_url(
    payload: SignedDownloadRequest,
    auth: AuthContext = Depends(require_org_context),
    db: AsyncSession = Depends(get_db_session),
) -> SignedDownloadResponse:
    doc_result = await db.execute(
        select(Document).where(
            Document.org_id == auth.active_org_id,
            Document.storage_key == payload.storage_key,
        )
    )
    if doc_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found in active org")

    download_url = await run_in_threadpool(create_download_url, payload.storage_key)
    return SignedDownloadResponse(
        storage_key=payload.storage_key,
        download_url=download_url,
        expires_in_seconds=settings.s3_presign_expiry_seconds,
    )
