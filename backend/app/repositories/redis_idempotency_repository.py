from __future__ import annotations

from redis import Redis

from app.core.config import get_settings


class RedisIdempotencyRepository:
    def __init__(self, redis_url: str | None = None) -> None:
        settings = get_settings()
        self.client = Redis.from_url(redis_url or settings.redis_url, decode_responses=True)

    def get(self, key: str) -> str | None:
        value = self.client.get(key)
        if value is None:
            return None
        return str(value)

    def set(self, key: str, value: str, ttl_seconds: int) -> None:
        self.client.setex(key, ttl_seconds, value)

    def clear(self) -> None:
        raise RuntimeError("clear() is disabled for Redis idempotency persistence.")
