import pytest
import uuid
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient
from datetime import datetime, timezone
from app.models.link import Link


# тут тоже было необходимо жесткое вмешательство искусственного интеллекта
@pytest.mark.asyncio
async def test_redirect_link_in_cache(client, db):
    short_code = f"code-{uuid.uuid4()}"
    original_url = f"https://example.com/{uuid.uuid4()}"
    link = Link(short_code=short_code, original_url=original_url)
    db.add(link)
    db.commit()
    db.refresh(link)

    cached_data = {
        "original_url": original_url,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "access_count": "0",
        "last_accessed": datetime.now(timezone.utc).isoformat(),
    }

    async def hgetall_mock(key):
        if key == f"link:{short_code}":
            return cached_data
        return {}

    async_mock_redis = AsyncMock()
    async_mock_redis.hgetall.side_effect = hgetall_mock
    async_mock_redis.hset = AsyncMock()
    async_mock_redis.expire = AsyncMock()

    with patch("app.cache.redis", async_mock_redis):
        response = await client.get(f"/api/links/{short_code}")

    assert response.status_code == 200
    data = response.json()
    assert data["original_url"] == original_url


# и тут. С кэшем тяжело, но я стараюсь разобраться.
@pytest.mark.asyncio
async def test_redirect_link_in_db_only(client, db):
    short_code = f"code-{uuid.uuid4()}"
    original_url = f"https://example.com/{uuid.uuid4()}"
    link = Link(short_code=short_code, original_url=original_url)
    db.add(link)
    db.commit()
    db.refresh(link)

    with patch("app.services.link_service.redis", mock_redis_f()):
        response = await client.get(f"/api/links/{short_code}")

    assert response.status_code == 200
    data = response.json()
    assert data["original_url"] == original_url


@pytest.mark.asyncio
async def test_redirect_link_not_found(client: AsyncClient):
    short_code = "nonexistent"

    with patch("app.services.link_service.redis", mock_redis_f()):
        response = await client.get(f"/api/links/{short_code}")

    assert response.status_code == 404
    data = response.json()
    assert "Link not found" in data["detail"]


def mock_redis_f():
    mock_redis = AsyncMock()
    mock_redis.hgetall.return_value = None  # эмулируем пустой кэш
    mock_redis.hset.return_value = None
    mock_redis.expire.return_value = None

    return mock_redis
