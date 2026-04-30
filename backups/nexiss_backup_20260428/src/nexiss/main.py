from contextlib import asynccontextmanager

from fastapi import FastAPI

from nexiss.api.router import api_router
from nexiss.core.config import get_settings
from nexiss.core.logging import configure_logging
from nexiss.core.metrics import metrics_middleware
from nexiss.core.observability import configure_observability

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging(settings.log_level)
    configure_observability()
    yield


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    lifespan=lifespan,
)

app.middleware("http")(metrics_middleware)
app.include_router(api_router, prefix=settings.api_v1_prefix)
