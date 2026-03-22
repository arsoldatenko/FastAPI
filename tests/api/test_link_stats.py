# здесь по факту переиспользуем ручку, но проверим с статс

import pytest
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch
from types import SimpleNamespace

from app.models.link import Link


@pytest.mark.asyncio
async def test_link_stats_success(client, db):
    short_code = f"code-{uuid.uuid4()}"
    original_url = f"https://example.com/{uuid.uuid4()}"
    link = Link(short_code=short_code, original_url=original_url)
    link.created_at = datetime.now(timezone.utc)
    link.last_accessed = None
    link.access_count = 0
    db.add(link)
    db.commit()
    db.refresh(link)

    async_mock_redis = AsyncMock()
    async_mock_redis.hgetall.return_value = {
        "original_url": original_url,
        "created_at": link.created_at.isoformat(),
        "access_count": "0",
        "last_accessed": "",
    }
    async_mock_redis.hset.return_value = True

    with patch("app.services.link_service.redis", async_mock_redis):
        response = await client.get(f"/api/links/{short_code}/stats")

    assert response.status_code == 200
    data = response.json()
    assert data["original_url"] == original_url
    assert data["access_count"] == 0
    assert data["created_at"] == link.created_at.isoformat()
    assert data["last_accessed"] is None or isinstance(data["last_accessed"], str)

    async_mock_redis.hset.assert_awaited()


@pytest.mark.asyncio
async def test_link_stats_not_found(client, db):
    short_code = "nonexistent"

    # Мокируем Redis, чтобы вернуть пустой результат
    async_mock_redis = AsyncMock()
    async_mock_redis.hgetall.return_value = {}

    with patch("app.services.link_service.redis", async_mock_redis):
        response = await client.get(f"/api/links/{short_code}/stats")

    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Link not found"
