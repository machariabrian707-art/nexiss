import pytest


@pytest.mark.asyncio
async def test_admin_requires_superadmin(client):
    # Regular user should get 403
    await client.post("/api/v1/auth/register", json={
        "email": "regular@nexiss.io",
        "password": "password123",
        "full_name": "Regular User",
        "org_name": "Regular Org",
    })
    login = await client.post("/api/v1/auth/login", json={
        "email": "regular@nexiss.io",
        "password": "password123",
    })
    token = login.json()["access_token"]

    resp = await client.get(
        "/api/v1/admin/stats",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403
