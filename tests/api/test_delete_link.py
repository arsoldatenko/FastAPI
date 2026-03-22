import pytest
import uuid
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient
from app.models.link import Link


@pytest.mark.asyncio
async def test_delete_link_success(client: AsyncClient, db):
    short_code = f"code-{uuid.uuid4()}"
    original_url = f"https://example.com/{uuid.uuid4()}"
    link = Link(short_code=short_code, original_url=original_url)
    db.add(link)
    db.commit()
    db.refresh(link)

    async_mock_redis = AsyncMock()
    async_mock_redis.delete = AsyncMock(return_value=1)

    with patch("app.services.link_service.redis", async_mock_redis):
        response = await client.delete(f"api/links/{short_code}")

    assert response.status_code == 200
    data = response.json()
    assert data["detail"] == "Ссылка удалена"

    link_in_db = db.query(Link).filter(Link.short_code == short_code).first()
    assert link_in_db is None

    async_mock_redis.delete.assert_awaited_with(f"link:{short_code}")


@pytest.mark.asyncio
async def test_delete_link_not_found(client: AsyncClient):
    short_code = "nonexistent"

    async_mock_redis = AsyncMock()
    async_mock_redis.delete.return_value = 0

    with patch("app.cache.redis", async_mock_redis):
        response = await client.delete(f"/links/{short_code}")

    assert response.status_code == 404
    data = response.json()
    assert "Not Found" in data["detail"]
