from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.sql import func
from app.database import Base


class Link(Base):
    __tablename__ = "links"

    short_code = Column(String, primary_key=True, index=True)
    original_url = Column(String, nullable=False, unique=True)
    custom_alias = Column(String, unique=True, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    last_accessed = Column(DateTime, nullable=True)
    access_count = Column(Integer, default=0)
    expires_at = Column(DateTime, nullable=True)
