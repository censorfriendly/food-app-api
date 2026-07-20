import pytest
import pytest_asyncio
from httpx import AsyncClient


@pytest.mark.anyio
async def test_fake_login(async_client: AsyncClient):
    response = await async_client.post("/api/v1/auth/fake-login", json={"email": "test@example.com"})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data["data"]
    assert "refresh_token" in data["data"]
    assert data["data"]["user"]["email"] == "test@example.com"


@pytest.mark.anyio
async def test_fake_login_default_email(async_client: AsyncClient):
    response = await async_client.post("/api/v1/auth/fake-login", json={})
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["user"]["email"] == "dev@example.com"
