from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime


class LinkCreate(BaseModel):
    original_url: HttpUrl
    custom_alias: Optional[str] = None
    expires_at: Optional[datetime] = None


class LinkUpdate(BaseModel):
    original_url: Optional[HttpUrl] = None


class LinkStats(BaseModel):
    original_url: str
    created_at: datetime
    last_accessed: Optional[datetime]
    access_count: int
