import pytest
import uuid
from httpx import AsyncClient
from app.models.link import Link
from app.database import get_db
from sqlalchemy.orm import Session


@pytest.mark.asyncio
async def test_search_existing_link(client: AsyncClient, db: Session):

    original_url = f"https://example.com/{uuid.uuid4()}"
    link = Link(short_code="testcode", original_url=original_url)
    db.add(link)
    db.commit()
    db.refresh(link)

    response = await client.get(
        "/api/links/search", params={"original_url": original_url}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["short_code"] == "testcode"
    assert data[0]["original_url"].rstrip("/") == original_url.rstrip("/")


@pytest.mark.asyncio
async def test_search_nonexistent_link(client: AsyncClient):
    # Делаем запрос к несуществующей ссылке
    response = await client.get(
        "/api/links/search", params={"original_url": "https://notfound.com"}
    )
    assert response.status_code == 404
    data = response.json()
    assert "Link not found" in data["detail"]
