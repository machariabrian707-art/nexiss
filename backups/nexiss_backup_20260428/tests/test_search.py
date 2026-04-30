import pytest


@pytest.mark.asyncio
async def test_search_requires_auth(client):
    resp = await client.get("/api/v1/search?q=invoice")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_search_returns_list(client):
    await client.post("/api/v1/auth/register", json={
        "email": "search@nexiss.io",
        "password": "password123",
        "full_name": "Search User",
        "org_name": "Search Org",
    })
    login = await client.post("/api/v1/auth/login", json={
        "email": "search@nexiss.io",
        "password": "password123",
    })
    token = login.json()["access_token"]

    resp = await client.get(
        "/api/v1/search?q=invoice",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
