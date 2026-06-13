from __future__ import annotations

from functools import lru_cache

from app.core.config import get_settings
from app.repositories.idempotency_repository import (
    IdempotencyRepository,
    InMemoryIdempotencyRepository,
)
from app.repositories.redis_idempotency_repository import RedisIdempotencyRepository


@lru_cache(maxsize=1)
def get_idempotency_repository() -> IdempotencyRepository:
    settings = get_settings()
    if settings.idempotency_store == "redis":
        return RedisIdempotencyRepository()
    if settings.idempotency_store == "in_memory":
        return InMemoryIdempotencyRepository()

    raise ValueError("IDEMPOTENCY_STORE must be either 'in_memory' or 'redis'.")


def reset_idempotency_repository_cache() -> None:
    get_idempotency_repository.cache_clear()
