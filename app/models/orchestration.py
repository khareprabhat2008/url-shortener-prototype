from __future__ import annotations

from datetime import datetime

from sqlalchemy import String, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ClickEvent(Base):
    __tablename__ = "click_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: __import__('uuid').uuid4().hex)
    short_url_id: Mapped[str] = mapped_column(String(36), ForeignKey("short_urls.id"), nullable=False, index=True)
    alias: Mapped[str] = mapped_column(String(64), nullable=False)
    target_url: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    country: Mapped[str | None] = mapped_column(String(64), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
