from __future__ import annotations

from app.core.config import get_settings
from app.repositories.idempotency_factory import get_idempotency_repository
from app.repositories.idempotency_repository import IdempotencyRepository
from app.schemas.prediction import PredictionResponse


class IdempotencyService:
    def __init__(
        self,
        repository: IdempotencyRepository | None = None,
        ttl_seconds: int | None = None,
    ) -> None:
        settings = get_settings()
        self.repository = repository or get_idempotency_repository()
        self.ttl_seconds = ttl_seconds or settings.idempotency_ttl_seconds

    def get_response(self, key: str) -> PredictionResponse | None:
        raw_value = self.repository.get(normalize_key(key))
        if raw_value is None:
            return None
        return PredictionResponse.model_validate_json(raw_value)

    def store_response(self, key: str, response: PredictionResponse) -> None:
        self.repository.set(
            normalize_key(key),
            response.model_dump_json(),
            ttl_seconds=self.ttl_seconds,
        )


def normalize_key(key: str) -> str:
    return f"predict:{key.strip()}"
