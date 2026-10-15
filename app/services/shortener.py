import json
from typing import Any

import redis.asyncio as redis

from app.core.config import settings

redis_client = redis.from_url(settings.redis_url, decode_responses=True)


async def enqueue_click_event(payload: dict[str, Any]) -> None:
    await redis_client.lpush("click_events", json.dumps(payload))
