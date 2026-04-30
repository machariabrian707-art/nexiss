from httpx import ASGITransport, AsyncClient

from nexiss.main import app


async def test_metrics_endpoint_returns_prometheus_text() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/metrics")

    assert response.status_code == 200
    assert "nexiss_http_requests_total" in response.text

