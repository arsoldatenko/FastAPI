import pytest
import uuid
from httpx import AsyncClient
from app.main import app
from app.database import SessionLocal, Base, engine
from app.models.link import Link


@pytest.mark.anyio
async def test_shorten_link_success(client):
    payload = {"original_url": "https://example.com/"}
    response = await client.post("api/links/shorten", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "short_code" in data
    assert data["original_url"] == payload["original_url"]


@pytest.mark.asyncio
async def test_shorten_link_with_custom_alias(client: AsyncClient):
    url = f"https://example.com/{uuid.uuid4()}"
    custom_alias = "myalias"
    response = await client.post(
        "/api/links/shorten",
        json={"original_url": url, "custom_alias": custom_alias, "expires_at": None},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["short_code"] == custom_alias
    assert data["original_url"].rstrip("/") == url.rstrip("/")


@pytest.mark.asyncio
async def test_shorten_link_invalid_url(client: AsyncClient):
    response = await client.post(
        "/api/links/shorten",
        json={
            "original_url": "not-a-valid-url",
            "custom_alias": None,
            "expires_at": None,
        },
    )
    assert response.status_code == 422


# здесь проверим два запроса один упадет другой не упадет
@pytest.mark.asyncio
async def test_shorten_link_duplicate_alias(client: AsyncClient):
    url1 = f"https://example.com/{uuid.uuid4()}"
    url2 = f"https://example.com/{uuid.uuid4()}"
    custom_alias = "dupalias"

    response1 = await client.post(
        "/api/links/shorten",
        json={"original_url": url1, "custom_alias": custom_alias, "expires_at": None},
    )
    assert response1.status_code == 200

    response2 = await client.post(
        "/api/links/shorten",
        json={"original_url": url2, "custom_alias": custom_alias, "expires_at": None},
    )
    assert response2.status_code == 400
    assert "Ссылка уже существует" in response2.json()["detail"]


# тут помогла жоско нейронка
@pytest.mark.asyncio
async def test_shorten_link_service_error(client: AsyncClient):
    url = f"https://example.com/{uuid.uuid4()}"
    custom_alias = "erroralias"

    response = await client.post(
        "/api/links/shorten",
        json={"original_url": url, "custom_alias": custom_alias, "expires_at": None},
    )
    assert response.status_code == 200

    response_dup = await client.post(
        "/api/links/shorten",
        json={
            "original_url": f"{url}-2",
            "custom_alias": custom_alias,
            "expires_at": None,
        },
    )
    assert response_dup.status_code == 400
    assert "Ссылка уже существует" in response_dup.json()["detail"]
