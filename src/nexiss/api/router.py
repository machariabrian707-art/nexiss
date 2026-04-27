from fastapi import APIRouter

from nexiss.api.v1 import (
    admin,
    analytics,
    auth,
    billing,
    documents,
    export,
    health,
    metrics,
    realtime,
    search,
    storage,
    tenancy,
    usage,
)

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(tenancy.router)
api_router.include_router(storage.router)
api_router.include_router(documents.router)
api_router.include_router(search.router)
api_router.include_router(export.router)
api_router.include_router(usage.router)
api_router.include_router(analytics.router)
api_router.include_router(billing.router)
api_router.include_router(metrics.router)
api_router.include_router(realtime.router)
api_router.include_router(admin.router)
