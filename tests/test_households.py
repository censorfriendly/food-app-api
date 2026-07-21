import pytest
from httpx import AsyncClient

from models.user import User
from services.household_service import HouseholdService


@pytest.mark.anyio
async def test_create_household_for_authenticated_user(async_client: AsyncClient):
    auth_response = await async_client.post(
        "/api/v1/auth/fake-login",
        json={"email": "household@example.com"},
    )
    assert auth_response.status_code == 200

    token = auth_response.json()["data"]["access_token"]
    response = await async_client.post(
        "/api/v1/households",
        json={"name": "The Smith Family", "timezone": "America/New_York"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["name"] == "The Smith Family"
    assert payload["data"]["owner"]["email"] == "household@example.com"


@pytest.mark.anyio
async def test_list_user_households(async_client: AsyncClient):
    auth_response = await async_client.post(
        "/api/v1/auth/fake-login",
        json={"email": "households@example.com"},
    )
    assert auth_response.status_code == 200

    token = auth_response.json()["data"]["access_token"]
    response = await async_client.get(
        "/api/v1/households",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert len(payload["data"]) >= 1
    assert any(item["is_default"] for item in payload["data"])


@pytest.mark.anyio
async def test_set_default_household(async_client: AsyncClient, db_session):
    auth_response = await async_client.post(
        "/api/v1/auth/fake-login",
        json={"email": "household-default@example.com"},
    )
    assert auth_response.status_code == 200

    token = auth_response.json()["data"]["access_token"]
    user = db_session.query(User).filter(User.email == "household-default@example.com").one()
    service = HouseholdService(db_session)
    second_household = service.create_household(user, "Second Home", "UTC")

    response = await async_client.patch(
        "/api/v1/households/default",
        json={"household_id": second_household["id"]},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["household_id"] == second_household["id"]

    list_response = await async_client.get(
        "/api/v1/households",
        headers={"Authorization": f"Bearer {token}"},
    )
    households = list_response.json()["data"]
    assert any(item["id"] == second_household["id"] and item["is_default"] for item in households)


@pytest.mark.anyio
async def test_invite_user_to_household(async_client: AsyncClient, db_session):
    auth_response = await async_client.post(
        "/api/v1/auth/fake-login",
        json={"email": "inviter@example.com"},
    )
    assert auth_response.status_code == 200

    token = auth_response.json()["data"]["access_token"]
    user = db_session.query(User).filter(User.email == "inviter@example.com").one()
    service = HouseholdService(db_session)
    household = service.create_household(user, "Invite House", "UTC")

    response = await async_client.post(
        f"/api/v1/households/{household['id']}/invite",
        json={"email": "household-default@example.com"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["status"] == "joined"
    assert payload["data"]["email"] == "household-default@example.com"
