from __future__ import annotations

from datetime import timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from nexiss.api.deps.auth import AuthContext, get_auth_context
from nexiss.core.config import get_settings
from nexiss.core.security import create_access_token, get_password_hash, verify_password
from nexiss.db.models.org_membership import MembershipRole, MembershipStatus, OrgMembership
from nexiss.db.models.organization import Organization
from nexiss.db.models.user import User
from nexiss.db.session import get_db_session
from nexiss.schemas.auth import (
    CurrentUserResponse,
    LoginRequest,
    RegisterRequest,
    SwitchOrgRequest,
    TokenResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


async def _resolve_user_memberships(user_id: UUID, db: AsyncSession) -> list[UUID]:
    rows = await db.execute(
        select(OrgMembership.org_id).where(
            OrgMembership.user_id == user_id,
            OrgMembership.status == MembershipStatus.active,
        )
    )
    return [row[0] for row in rows.all()]


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterRequest, db: AsyncSession = Depends(get_db_session)
) -> TokenResponse:
    existing_org = await db.execute(
        select(Organization).where(Organization.slug == payload.org_slug)
    )
    if existing_org.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Organisation slug already taken — choose a different one",
        )

    existing_user = await db.execute(select(User).where(User.email == payload.email))
    if existing_user.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )

    # Create org first and flush so org_id PK is available for FK references
    organization = Organization(name=payload.org_name, slug=payload.org_slug)
    db.add(organization)
    await db.flush()          # org_id now guaranteed to exist in the session

    user = User(
        org_id=organization.org_id,
        email=payload.email,
        password_hash=get_password_hash(payload.password),
        full_name=payload.full_name,
        is_active=True,
        is_superuser=False,
    )
    db.add(user)
    await db.flush()          # user.id now available for membership FK

    membership = OrgMembership(
        org_id=organization.org_id,
        user_id=user.id,
        role=MembershipRole.owner,
        status=MembershipStatus.active,
    )
    db.add(membership)
    await db.commit()
    await db.refresh(user)

    expires_delta = timedelta(minutes=settings.jwt_access_token_expire_minutes)
    token = create_access_token(
        user_id=user.id, org_id=organization.org_id, expires_delta=expires_delta
    )
    return TokenResponse(
        access_token=token, expires_in_seconds=int(expires_delta.total_seconds())
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest, db: AsyncSession = Depends(get_db_session)
) -> TokenResponse:
    user_result = await db.execute(select(User).where(User.email == payload.email))
    user = user_result.scalar_one_or_none()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive"
        )

    memberships = await _resolve_user_memberships(user.id, db)
    if not memberships and not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No active organisation membership found",
        )

    target_org_id = payload.org_id or (memberships[0] if memberships else user.org_id)
    if not user.is_superuser and target_org_id not in memberships:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Requested org not available"
        )

    expires_delta = timedelta(minutes=settings.jwt_access_token_expire_minutes)
    token = create_access_token(
        user_id=user.id, org_id=target_org_id, expires_delta=expires_delta
    )
    return TokenResponse(
        access_token=token, expires_in_seconds=int(expires_delta.total_seconds())
    )


@router.post("/switch-org", response_model=TokenResponse)
async def switch_org(
    payload: SwitchOrgRequest,
    auth: AuthContext = Depends(get_auth_context),
) -> TokenResponse:
    if payload.org_id not in auth.memberships:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Org access denied")

    expires_delta = timedelta(minutes=settings.jwt_access_token_expire_minutes)
    token = create_access_token(
        user_id=auth.user.id, org_id=payload.org_id, expires_delta=expires_delta
    )
    return TokenResponse(
        access_token=token, expires_in_seconds=int(expires_delta.total_seconds())
    )


@router.get("/me", response_model=CurrentUserResponse)
async def me(auth: AuthContext = Depends(get_auth_context)) -> CurrentUserResponse:
    active_org_role = auth.active_org_role.value if auth.active_org_role else None
    return CurrentUserResponse(
        user_id=auth.user.id,
        email=auth.user.email,
        full_name=auth.user.full_name,
        is_superuser=auth.user.is_superuser,    # now included
        active_org_id=auth.active_org_id,
        active_org_role=active_org_role,
        can_process_documents=auth.user.is_superuser or active_org_role in {"owner", "admin"},
        memberships=sorted(auth.memberships, key=str),
        authenticated_at=auth.authenticated_at,
    )
