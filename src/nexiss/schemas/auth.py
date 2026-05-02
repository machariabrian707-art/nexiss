"""Auth schemas — fix: add is_superuser to CurrentUserResponse so the
frontend authStore receives it and can route to /admin correctly.
"""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
    org_name: str = Field(min_length=2, max_length=255)
    org_slug: str = Field(min_length=2, max_length=120, pattern=r"^[a-z0-9-]+$")
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    org_id: UUID | None = None


class SwitchOrgRequest(BaseModel):
    org_id: UUID


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_seconds: int


class CurrentUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    email: EmailStr
    full_name: str | None
    is_superuser: bool            # <— added: frontend needs this to route to /admin
    active_org_id: UUID
    active_org_role: str | None
    can_process_documents: bool
    memberships: list[UUID]
    authenticated_at: datetime
