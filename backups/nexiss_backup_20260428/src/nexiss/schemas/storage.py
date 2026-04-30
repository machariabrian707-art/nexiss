from __future__ import annotations

from pydantic import BaseModel, Field


class SignedUploadRequest(BaseModel):
    file_name: str = Field(min_length=1, max_length=255)
    content_type: str


class SignedUploadResponse(BaseModel):
    storage_key: str
    upload_url: str
    expires_in_seconds: int
    required_headers: dict[str, str]


class SignedDownloadRequest(BaseModel):
    storage_key: str


class SignedDownloadResponse(BaseModel):
    storage_key: str
    download_url: str
    expires_in_seconds: int
