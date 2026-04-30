from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from uuid import UUID, uuid4

import boto3
from botocore.client import BaseClient

from nexiss.core.config import get_settings

settings = get_settings()
ALLOWED_DOCUMENT_CONTENT_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
}


@lru_cache(maxsize=1)
def get_s3_client() -> BaseClient:
    kwargs: dict[str, str] = {
        "region_name": settings.s3_region,
    }
    if settings.s3_access_key_id and settings.s3_secret_access_key:
        kwargs["aws_access_key_id"] = settings.s3_access_key_id
        kwargs["aws_secret_access_key"] = settings.s3_secret_access_key
    if settings.s3_endpoint_url:
        kwargs["endpoint_url"] = settings.s3_endpoint_url

    return boto3.client("s3", **kwargs)


def validate_content_type(content_type: str) -> None:
    if content_type not in ALLOWED_DOCUMENT_CONTENT_TYPES:
        supported = ", ".join(sorted(ALLOWED_DOCUMENT_CONTENT_TYPES))
        raise ValueError(f"Unsupported content type. Supported: {supported}")


def build_storage_key(org_id: UUID, file_name: str) -> str:
    safe_name = Path(file_name).name
    return f"{org_id}/raw/{uuid4()}-{safe_name}"


def create_upload_url(storage_key: str, content_type: str) -> str:
    client = get_s3_client()
    return client.generate_presigned_url(
        ClientMethod="put_object",
        Params={
            "Bucket": settings.s3_bucket,
            "Key": storage_key,
            "ContentType": content_type,
        },
        ExpiresIn=settings.s3_presign_expiry_seconds,
    )


def create_download_url(storage_key: str) -> str:
    client = get_s3_client()
    return client.generate_presigned_url(
        ClientMethod="get_object",
        Params={
            "Bucket": settings.s3_bucket,
            "Key": storage_key,
        },
        ExpiresIn=settings.s3_presign_expiry_seconds,
    )
