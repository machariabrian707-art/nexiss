import pytest


@pytest.mark.asyncio
async def test_analytics_requires_auth(client):
    resp = await client.get("/api/v1/analytics/overview")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_analytics_overview(client):
    # Register + login
    await client.post("/api/v1/auth/register", json={
        "email": "analytics@nexiss.io",
        "password": "password123",
        "full_name": "Analytics User",
        "org_name": "Analytics Org",
    })
    login = await client.post("/api/v1/auth/login", json={
        "email": "analytics@nexiss.io",
        "password": "password123",
    })
    token = login.json()["access_token"]

    resp = await client.get(
        "/api/v1/analytics/overview",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "total_documents" in data
    assert "completed" in data
    assert "failed" in data
