import pytest


@pytest.mark.asyncio
async def test_register_and_login(client):
    # Register
    resp = await client.post("/api/v1/auth/register", json={
        "email": "test@nexiss.io",
        "password": "testpassword123",
        "full_name": "Test User",
        "org_name": "Test Org",
    })
    assert resp.status_code in (200, 201), resp.text

    # Login
    resp = await client.post("/api/v1/auth/login", json={
        "email": "test@nexiss.io",
        "password": "testpassword123",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    return data["access_token"]


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    # Register first
    await client.post("/api/v1/auth/register", json={
        "email": "wrong@nexiss.io",
        "password": "rightpass",
        "full_name": "Wrong User",
        "org_name": "Wrong Org",
    })
    # Login with wrong password
    resp = await client.post("/api/v1/auth/login", json={
        "email": "wrong@nexiss.io",
        "password": "wrongpass",
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_requires_auth(client):
    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_with_token(client):
    # Register + login
    await client.post("/api/v1/auth/register", json={
        "email": "me@nexiss.io",
        "password": "password123",
        "full_name": "Me User",
        "org_name": "Me Org",
    })
    login = await client.post("/api/v1/auth/login", json={
        "email": "me@nexiss.io",
        "password": "password123",
    })
    token = login.json()["access_token"]

    resp = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["email"] == "me@nexiss.io"
