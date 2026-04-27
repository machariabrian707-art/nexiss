from httpx import ASGITransport, AsyncClient

from nexiss.main import app


async def test_health_endpoint() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] in {"ok", "degraded"}
    assert "checks" in payload
    assert "database" in payload["checks"]
    assert "redis" in payload["checks"]
