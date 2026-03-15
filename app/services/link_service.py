from sqlalchemy.orm import Session
from datetime import datetime, timezone
import random, string
from app.models.link import Link
from app.cache import redis
from types import SimpleNamespace

CACHE_TTL = 60 * 60


def generate_short_code(length=6):
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def create_link(
    db: Session,
    original_url: str,
    custom_alias: str = None,
    expires_at: datetime = None,
):
    short_code = custom_alias or generate_short_code()
    # Проверка уникальности
    if (
        db.query(Link)
        .filter((Link.short_code == short_code) | (Link.custom_alias == custom_alias))
        .first()
    ):
        raise ValueError("Ссылка уже существует")

    link = Link(
        short_code=short_code,
        original_url=str(original_url),
        custom_alias=custom_alias,
        expires_at=expires_at,
    )
    db.add(link)
    db.commit()
    db.refresh(link)
    return link


async def get_link(db: Session, short_code: str):
    key = f"link:{short_code}"

    # Здесь жоско нагенерил, т.к. была проблема с тем, что функция переиспользуется в двух ручках и в одной нужно только одно поле, а в другой весь объект
    # Попытка взять из кэша
    cached = await redis.hgetall(key)
    if cached:
        # Преобразуем обратно в объект
        link = SimpleNamespace(
            short_code=short_code,
            original_url=cached["original_url"],
            created_at=datetime.fromisoformat(cached["created_at"]),
            access_count=int(cached["access_count"]),
            last_accessed=(
                datetime.fromisoformat(cached["last_accessed"])
                if cached["last_accessed"]
                else None
            ),
        )

        # Обновляем счетчик в БД
        db_link = db.query(Link).filter(Link.short_code == short_code).first()
        if db_link:
            db_link.access_count += 1
            db_link.last_accessed = datetime.now(timezone.utc)
            db.commit()

            # Обновляем кэш с новыми значениями
            await redis.hset(
                key,
                mapping={
                    "original_url": db_link.original_url,
                    "created_at": db_link.created_at.isoformat(),
                    "access_count": str(db_link.access_count),
                    "last_accessed": db_link.last_accessed.isoformat(),
                },
            )

        return link

    # Если в кэше нет, берём из базы
    link = db.query(Link).filter(Link.short_code == short_code).first()
    if link:
        link.access_count += 1
        link.last_accessed = datetime.now(timezone.utc)
        db.commit()

        # Сохраняем в кэш все поля
        await redis.hset(
            key,
            mapping={
                "original_url": link.original_url,
                "created_at": link.created_at.isoformat(),
                "access_count": str(link.access_count),
                "last_accessed": link.last_accessed.isoformat(),
            },
        )
        await redis.expire(key, CACHE_TTL)

        return link


async def delete_link(db: Session, short_code: str):
    link = db.query(Link).filter(Link.short_code == short_code).first()
    if link:
        db.delete(link)
        db.commit()
        await redis.delete(f"link:{short_code}")
    return link


async def update_link(
    db: Session, short_code: str, new_url: str = None, expires_at: datetime = None
):
    link = db.query(Link).filter(Link.short_code == short_code).first()
    if link:
        if new_url:
            link.original_url = str(new_url)
        db.commit()
        db.refresh(link)
        await redis.set(f"link:{short_code}", link.original_url, ex=CACHE_TTL)
    return link


def search_link(db: Session, original_url: str):
    return db.query(Link).filter(Link.original_url == original_url).first()
