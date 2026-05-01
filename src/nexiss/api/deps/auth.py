from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from nexiss.core.security import decode_token
from nexiss.db.models.org_membership import MembershipStatus, OrgMembership
from nexiss.db.models.user import User
from nexiss.db.session import get_db_session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


@dataclass(slots=True)
class AuthContext:
    user: User
    active_org_id: UUID
    memberships: set[UUID]
    authenticated_at: datetime


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db_session),
) -> User:
    ctx = await resolve_auth_context_from_token(token, db)
    return ctx.user


async def _load_memberships(user_id: UUID, db: AsyncSession) -> set[UUID]:
    result = await db.execute(
        select(OrgMembership.org_id).where(
            OrgMembership.user_id == user_id,
            OrgMembership.status == MembershipStatus.active,
        )
    )
    return {row[0] for row in result.all()}


async def get_auth_context(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db_session),
) -> AuthContext:
    return await resolve_auth_context_from_token(token, db)


async def resolve_auth_context_from_token(token: str, db: AsyncSession) -> AuthContext:
    try:
        payload = decode_token(token)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        ) from exc

    sub = payload.get("sub")
    org_claim = payload.get("org_id")
    if sub is None or org_claim is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload"
        )

    user = await db.get(User, UUID(sub))
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive or missing user"
        )

    memberships = await _load_memberships(user.id, db)
    active_org_id = UUID(org_claim)

    if active_org_id not in memberships:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Token org access revoked"
        )

    return AuthContext(
        user=user,
        active_org_id=active_org_id,
        memberships=memberships,
        authenticated_at=datetime.now(UTC),
    )


async def require_org_context(
    auth: AuthContext = Depends(get_auth_context),
    # X-Org-Id is OPTIONAL — if not provided we use the org from the JWT token.
    # This prevents 422 errors immediately after login before the frontend
    # has stored the activeOrgId in state.
    x_org_id: str | None = Header(default=None, alias="X-Org-Id"),
) -> AuthContext:
    if x_org_id is None:
        # No header — use the org from the JWT (already validated above)
        return auth

    try:
        requested_org_id = UUID(x_org_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid X-Org-Id header"
        ) from exc

    if requested_org_id not in auth.memberships:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Org access denied"
        )

    return AuthContext(
        user=auth.user,
        active_org_id=requested_org_id,
        memberships=auth.memberships,
        authenticated_at=auth.authenticated_at,
    )
