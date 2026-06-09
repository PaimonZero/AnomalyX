from __future__ import annotations

from dataclasses import dataclass
from json import JSONDecodeError
import logging

from app.core.config import get_settings
from app.repositories.idempotency_factory import get_idempotency_repository
from app.repositories.idempotency_repository import IdempotencyRepository
from app.schemas.prediction import PredictionResponse
from pydantic import ValidationError

PROCESSING_VALUE = "__processing__"
logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class IdempotencyClaim:
    is_claimed: bool
    response: PredictionResponse | None = None


class IdempotencyService:
    def __init__(
        self,
        repository: IdempotencyRepository | None = None,
        ttl_seconds: int | None = None,
    ) -> None:
        settings = get_settings()
        self.repository = repository or get_idempotency_repository()
        self.ttl_seconds = ttl_seconds if ttl_seconds is not None else settings.idempotency_ttl_seconds

    def get_response(self, key: str) -> PredictionResponse | None:
        normalized_key = normalize_key(key)
        raw_value = self.repository.get(normalized_key)
        if raw_value is None:
            return None
        if raw_value == PROCESSING_VALUE:
            return None
        return _parse_response(normalized_key, raw_value)

    def claim_response(self, key: str) -> IdempotencyClaim:
        normalized_key = normalize_key(key)
        is_claimed = self.repository.set_if_absent(
            normalized_key,
            PROCESSING_VALUE,
            ttl_seconds=self.ttl_seconds,
        )
        if is_claimed:
            return IdempotencyClaim(is_claimed=True)

        raw_value = self.repository.get(normalized_key)
        if raw_value is None:
            return IdempotencyClaim(is_claimed=False)
        if raw_value == PROCESSING_VALUE:
            return IdempotencyClaim(is_claimed=False)
        response = _parse_response(normalized_key, raw_value)
        if response is not None:
            return IdempotencyClaim(is_claimed=False, response=response)

        self.repository.delete(normalized_key)
        is_claimed = self.repository.set_if_absent(
            normalized_key,
            PROCESSING_VALUE,
            ttl_seconds=self.ttl_seconds,
        )
        return IdempotencyClaim(is_claimed=is_claimed)

    def store_response(self, key: str, response: PredictionResponse) -> None:
        self.repository.set(
            normalize_key(key),
            response.model_dump_json(),
            ttl_seconds=self.ttl_seconds,
        )

    def release_response_claim(self, key: str) -> None:
        self.repository.delete(normalize_key(key))


def normalize_key(key: str) -> str:
    stripped = key.strip()
    if not stripped:
        raise ValueError("idempotency key cannot be empty")
    return f"predict:{stripped}"


def _parse_response(normalized_key: str, raw_value: str) -> PredictionResponse | None:
    try:
        return PredictionResponse.model_validate_json(raw_value)
    except (ValidationError, JSONDecodeError):
        logger.warning(
            "Invalid idempotency response payload for key %s: %r",
            normalized_key,
            raw_value[:500],
        )
        return None
