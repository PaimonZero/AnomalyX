from __future__ import annotations

import hashlib
import json
import logging
from typing import Any

from redis import Redis
from app.core.config import get_settings
from app.llm.explainer import ExplanationResult
from app.schemas.alert import Alert

_logger = logging.getLogger(__name__)


class ExplanationCache:
    def __init__(self, redis_url: str | None = None) -> None:
        settings = get_settings()
        self.idempotency_store = settings.idempotency_store
        self.use_redis = self.idempotency_store == "redis"
        self.ttl = 3600  # 1 hour
        self.client = None

        if self.use_redis:
            try:
                self.client = Redis.from_url(
                    redis_url or settings.redis_url,
                    decode_responses=True,
                    socket_connect_timeout=settings.redis_socket_connect_timeout_seconds,
                    socket_timeout=settings.redis_socket_timeout_seconds,
                )
                self.client.ping()
                _logger.info("ExplanationCache successfully connected to Redis.")
            except Exception as e:
                _logger.warning(
                    f"Redis connection failed for explanation cache, falling back to in-memory: {e}"
                )
                self.use_redis = False

        if not self.use_redis:
            self._local_cache: dict[str, str] = {}

    def clear(self) -> None:
        if self.use_redis and self.client:
            try:
                keys = self.client.keys("anomalyx:exp_cache:*")
                if keys:
                    self.client.delete(*keys)
            except Exception as e:
                _logger.warning(f"Failed to clear Redis keys in clear(): {e}")
        else:
            if hasattr(self, "_local_cache"):
                self._local_cache.clear()

    def cache_key(self, alert: Alert) -> str:
        """Generate fingerprint hash based on sorted triggered rules and bucketed top features."""
        # Sort rule IDs
        rule_ids = sorted([rule.id for rule in alert.triggered_rules])

        # Bucket top features: name and contribution rounded to 1 decimal place
        bucketed_features = []
        for feature in alert.top_features:
            name = feature.name
            contrib = feature.contribution
            # Rounding to 1 decimal place buckets contributions (e.g. 0.31 and 0.34 both become 0.3)
            rounded_contrib = round(contrib, 1)
            bucketed_features.append(f"{name}:{rounded_contrib}")
        
        bucketed_features = sorted(bucketed_features)

        fingerprint = f"rules:{','.join(rule_ids)}|features:{','.join(bucketed_features)}"
        h = hashlib.md5(fingerprint.encode("utf-8")).hexdigest()
        return f"anomalyx:exp_cache:{h}"

    def get(self, alert: Alert) -> ExplanationResult | None:
        key = self.cache_key(alert)
        text = None

        if self.use_redis and self.client:
            try:
                text = self.client.get(key)
            except Exception as e:
                _logger.error(f"Error fetching from explanation cache: {e}", exc_info=True)
        else:
            text = self._local_cache.get(key)

        if text is not None:
            return ExplanationResult(text=text, source="cache")
        return None

    def set(self, alert: Alert, result: ExplanationResult) -> None:
        # We only cache successful LLM explanations (not templates or other cached ones)
        if result.source != "openai":
            return

        key = self.cache_key(alert)
        if self.use_redis and self.client:
            try:
                self.client.setex(key, self.ttl, result.text)
            except Exception as e:
                _logger.error(f"Error saving to explanation cache: {e}", exc_info=True)
        else:
            self._local_cache[key] = result.text


# Singleton instance
explanation_cache = ExplanationCache()
