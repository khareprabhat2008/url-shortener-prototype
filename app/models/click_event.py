from __future__ import annotations

from datetime import datetime

from sqlalchemy import String, DateTime, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ShortUrl(Base):
    __tablename__ = "short_urls"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: __import__('uuid').uuid4().hex)
    alias: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    original_url: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
