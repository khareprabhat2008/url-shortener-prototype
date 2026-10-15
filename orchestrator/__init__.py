from __future__ import annotations

import asyncio
import json
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import AsyncSessionFactory, init_db
from app.models.click_event import ClickEvent
from app.services.redis_manager import redis_client


async def process_click_events() -> None:
    while True:
        payload_raw = await redis_client.rpop("click_events")
        if payload_raw is None:
            await asyncio.sleep(0.5)
            continue

        payload = json.loads(payload_raw)
        async with AsyncSessionFactory() as session:
            click = ClickEvent(
                id=__import__('uuid').uuid4().hex,
                short_url_id=payload["short_url_id"],
                alias=payload.get("alias", ""),
                target_url=payload.get("target_url", ""),
                country=payload.get("country"),
                user_agent=payload.get("user_agent"),
                created_at=datetime.utcnow(),
            )
            session.add(click)
            await session.commit()


async def main() -> None:
    await init_db()
    await process_click_events()


if __name__ == "__main__":
    asyncio.run(main())
