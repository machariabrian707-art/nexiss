from fastapi import APIRouter
from redis.asyncio import Redis
from sqlalchemy import text

from nexiss.core.config import get_settings
from nexiss.db.session import engine

router = APIRouter(tags=["health"])
settings = get_settings()


@router.get("/health")
async def health_check() -> dict[str, object]:
    checks: dict[str, str] = {"database": "down", "redis": "down"}

    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception:
        checks["database"] = "down"

    try:
        redis = Redis.from_url(settings.redis_url, encoding="utf-8", decode_responses=True)
        pong = await redis.ping()
        await redis.aclose()
        checks["redis"] = "ok" if pong else "down"
    except Exception:
        checks["redis"] = "down"

    status = "ok" if all(value == "ok" for value in checks.values()) else "degraded"
    return {"status": status, "checks": checks}
