from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.services.link_service import (
    create_link,
    get_link,
    delete_link,
    update_link,
    search_link,
)
from app.schemas.link_schema import LinkCreate, LinkUpdate, LinkStats
from app.database import get_db

router = APIRouter()


@router.post("/links/shorten")
def shorten_link(link_data: LinkCreate, db: Session = Depends(get_db)):
    try:
        link = create_link(
            db, link_data.original_url, link_data.custom_alias, link_data.expires_at
        )
        return {"short_code": link.short_code, "original_url": link.original_url}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/links/search")
def search_links(original_url: str, db: Session = Depends(get_db)):
    link = search_link(db, original_url)
    print(link)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found1")
    return [{"short_code": link.short_code, "original_url": link.original_url}]


@router.get("/links/{short_code}")
async def redirect_link(short_code: str, db: Session = Depends(get_db)):
    link = await get_link(db, short_code)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    return {"original_url": link.original_url}


@router.delete("/links/{short_code}")
async def remove_link(short_code: str, db: Session = Depends(get_db)):
    link = await delete_link(db, short_code)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    return {"detail": "Ссылка удалена"}


@router.put("/links/{short_code}")
async def edit_link(
    short_code: str, link_data: LinkUpdate, db: Session = Depends(get_db)
):
    link = await update_link(db, short_code, link_data.original_url)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    return {"detail": "Сыдлка обновлена"}


@router.get("/links/{short_code}/stats")
async def link_stats(short_code: str, db: Session = Depends(get_db)):
    link = await get_link(db, short_code)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    return LinkStats(
        original_url=link.original_url,
        created_at=link.created_at,
        last_accessed=link.last_accessed,
        access_count=link.access_count,
    )
