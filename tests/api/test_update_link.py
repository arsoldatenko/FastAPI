import uuid
import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch
from datetime import datetime, timezone
from app.models.link import Link
from app.database import get_db
from app.services.link_service import CACHE_TTL


@pytest.mark.asyncio
async def test_edit_link_success(client: AsyncClient, db):
    short_code = f"code-{uuid.uuid4()}"
    original_url = f"https://example.com/{uuid.uuid4()}"
    link = Link(short_code=short_code, original_url=original_url)
    db.add(link)
    db.commit()
    db.refresh(link)

    new_url = f"https://new.example.com/{uuid.uuid4()}"

    # 1. Создаем AsyncMock для redis.set
    async_mock_redis = AsyncMock()
    async_mock_redis.set = AsyncMock(return_value=True)

    # 2. Патчим именно в модуле, где используется redis
    with patch("app.services.link_service.redis", async_mock_redis):
        response = await client.put(
            f"/api/links/{short_code}", json={"original_url": new_url}
        )

    # 3. Проверка ответа
    assert response.status_code == 200
    data = response.json()
    assert data["detail"] == "Ссылка обновлена"

    # 4. Проверка БД
    link_in_db = db.query(Link).filter(Link.short_code == short_code).first()
    assert link_in_db.original_url == new_url

    # 5. Проверка, что set был вызван
    async_mock_redis.set.assert_awaited_with(
        f"link:{short_code}", new_url, ex=CACHE_TTL
    )


@pytest.mark.asyncio
async def test_edit_link_not_found(client: AsyncClient):
    short_code = "nonexistent"
    new_url = "https://new.example.com"

    async_mock_redis = AsyncMock()

    with patch("app.services.link_service.redis", async_mock_redis):
        response = await client.put(
            f"/api/links/{short_code}", json={"original_url": new_url}
        )

    assert response.status_code == 404
    data = response.json()
    assert "Link not found" in data["detail"]
