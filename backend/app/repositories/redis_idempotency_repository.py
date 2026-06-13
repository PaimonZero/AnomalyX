from __future__ import annotations

from redis.backoff import ExponentialBackoff
from redis import Redis
from redis.retry import Retry

from app.core.config import get_settings


class RedisIdempotencyRepository:
    def __init__(self, redis_url: str | None = None) -> None:
        settings = get_settings()
        self.client = Redis.from_url(
            redis_url or settings.redis_url,
            decode_responses=True,
            socket_connect_timeout=settings.redis_socket_connect_timeout_seconds,
            socket_timeout=settings.redis_socket_timeout_seconds,
            retry_on_timeout=settings.redis_retry_on_timeout,
            retry=Retry(
                ExponentialBackoff(
                    base=settings.redis_retry_backoff_base_seconds,
                    cap=settings.redis_retry_backoff_cap_seconds,
                ),
                retries=settings.redis_retry_attempts,
            ),
        )

    def get(self, key: str) -> str | None:
        value = self.client.get(key)
        if value is None:
            return None
        return str(value)

    def set(self, key: str, value: str, ttl_seconds: int) -> None:
        self.client.setex(key, ttl_seconds, value)

    def set_if_absent(self, key: str, value: str, ttl_seconds: int) -> bool:
        return bool(self.client.set(key, value, ex=ttl_seconds, nx=True))

    def replace_if_value(
        self,
        key: str,
        expected_value: str,
        new_value: str,
        ttl_seconds: int,
    ) -> bool:
        script = """
        if redis.call("GET", KEYS[1]) == ARGV[1] then
            redis.call("SET", KEYS[1], ARGV[2], "EX", ARGV[3])
            return 1
        end
        return 0
        """
        return bool(self.client.eval(script, 1, key, expected_value, new_value, ttl_seconds))

    def delete(self, key: str) -> None:
        self.client.delete(key)

    def clear(self) -> None:
        raise RuntimeError("clear() is disabled for Redis idempotency persistence.")
