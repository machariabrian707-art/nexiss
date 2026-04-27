from fastapi import APIRouter

from nexiss.api.v1.analytics import router as analytics_router
from nexiss.api.v1.auth import router as auth_router
from nexiss.api.v1.billing import router as billing_router
from nexiss.api.v1.documents import router as documents_router
from nexiss.api.v1.health import router as health_router
from nexiss.api.v1.metrics import router as metrics_router
from nexiss.api.v1.realtime import router as realtime_router
from nexiss.api.v1.storage import router as storage_router
from nexiss.api.v1.tenancy import router as tenancy_router
from nexiss.api.v1.usage import router as usage_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(tenancy_router)
api_router.include_router(storage_router)
api_router.include_router(documents_router)
api_router.include_router(usage_router)
api_router.include_router(realtime_router)
api_router.include_router(analytics_router)
api_router.include_router(billing_router)
api_router.include_router(metrics_router)
