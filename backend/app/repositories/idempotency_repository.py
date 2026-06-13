from __future__ import annotations

from datetime import datetime, timedelta, timezone
from threading import Lock
from typing import Protocol


class IdempotencyRepository(Protocol):
    def get(self, key: str) -> str | None:
        """Return a stored response payload by idempotency key."""

    def set(self, key: str, value: str, ttl_seconds: int) -> None:
        """Store a response payload for a limited time."""

    def set_if_absent(self, key: str, value: str, ttl_seconds: int) -> bool:
        """Store a value only when the key does not already exist."""

    def replace_if_value(
        self,
        key: str,
        expected_value: str,
        new_value: str,
        ttl_seconds: int,
    ) -> bool:
        """Atomically replace a stored value when it still matches."""

    def delete(self, key: str) -> None:
        """Delete a stored key when supported."""

    def clear(self) -> None:
        """Clear stored keys when supported."""


class InMemoryIdempotencyRepository:
    def __init__(self) -> None:
        self._items: dict[str, tuple[str, datetime]] = {}
        self._lock = Lock()

    def get(self, key: str) -> str | None:
        now = datetime.now(timezone.utc)
        with self._lock:
            item = self._items.get(key)
            if item is None:
                return None
            value, expires_at = item
            if expires_at <= now:
                self._items.pop(key, None)
                return None
            return value

    def set(self, key: str, value: str, ttl_seconds: int) -> None:
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)
        with self._lock:
            self._items[key] = (value, expires_at)

    def set_if_absent(self, key: str, value: str, ttl_seconds: int) -> bool:
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(seconds=ttl_seconds)
        with self._lock:
            item = self._items.get(key)
            if item is not None:
                _, existing_expires_at = item
                if existing_expires_at > now:
                    return False
            self._items[key] = (value, expires_at)
            return True

    def replace_if_value(
        self,
        key: str,
        expected_value: str,
        new_value: str,
        ttl_seconds: int,
    ) -> bool:
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(seconds=ttl_seconds)
        with self._lock:
            item = self._items.get(key)
            if item is None:
                return False
            current_value, existing_expires_at = item
            if existing_expires_at <= now:
                self._items.pop(key, None)
                return False
            if current_value != expected_value:
                return False
            self._items[key] = (new_value, expires_at)
            return True

    def delete(self, key: str) -> None:
        with self._lock:
            self._items.pop(key, None)

    def clear(self) -> None:
        with self._lock:
            self._items.clear()


idempotency_repository = InMemoryIdempotencyRepository()
