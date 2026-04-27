from fastapi import APIRouter, Depends

from nexiss.api.deps.auth import AuthContext, require_org_context

router = APIRouter(prefix="/tenancy", tags=["tenancy"])


@router.get("/context")
async def tenancy_context(auth: AuthContext = Depends(require_org_context)) -> dict[str, str]:
    return {
        "user_id": str(auth.user.id),
        "active_org_id": str(auth.active_org_id),
    }
