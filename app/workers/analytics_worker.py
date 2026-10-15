from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.short_url import ShortUrl


class UrlShortenerService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_short_url(self, original_url: str, alias: str | None = None, expires_at: datetime | None = None) -> ShortUrl:
        if alias:
            existing = await self.session.get(ShortUrl, alias)
            if existing is not None:
                raise ValueError("Alias already exists")
        else:
            alias = await self._generate_alias()

        entity = ShortUrl(
            id=__import__('uuid').uuid4().hex,
            alias=alias,
            original_url=original_url,
            expires_at=expires_at,
        )
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def resolve_alias(self, alias: str) -> ShortUrl | None:
        result = await self.session.execute(select(ShortUrl).where(ShortUrl.alias == alias))
        return result.scalar_one_or_none()

    async def _generate_alias(self) -> str:
        base = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        alias = "" 
        for _ in range(8):
            alias += base[__import__('random').randint(0, len(base) - 1)]
        existing = await self.session.execute(select(ShortUrl).where(ShortUrl.alias == alias))
        if existing.scalar_one_or_none():
            return await self._generate_alias()
        return alias
