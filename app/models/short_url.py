from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.db.base import Base

if settings.database_url.startswith("sqlite"):
    engine = create_async_engine(settings.database_url, echo=False, connect_args={"check_same_thread": False})
else:
    engine = create_async_engine(settings.database_url, echo=False)

AsyncSessionFactory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def get_db_session() -> AsyncSession:
    return AsyncSessionFactory()
