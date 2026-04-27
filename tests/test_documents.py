import pytest


async def get_token(client, email="doc@nexiss.io", org="Doc Org"):
    await client.post("/api/v1/auth/register", json={
        "email": email,
        "password": "password123",
        "full_name": "Doc User",
        "org_name": org,
    })
    resp = await client.post("/api/v1/auth/login", json={
        "email": email,
        "password": "password123",
    })
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_documents_list_empty(client):
    token = await get_token(client, "doclist@nexiss.io", "DocList Org")
    resp = await client.get(
        "/api/v1/documents",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_documents_list_requires_auth(client):
    resp = await client.get("/api/v1/documents")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_document_not_found(client):
    token = await get_token(client, "docnotfound@nexiss.io", "DNF Org")
    resp = await client.get(
        "/api/v1/documents/00000000-0000-0000-0000-000000000000",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 404
