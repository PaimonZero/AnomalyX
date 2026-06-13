from concurrent.futures import ThreadPoolExecutor
import logging
import time

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.repositories.alert_repository import alert_repository
from app.repositories.idempotency_repository import InMemoryIdempotencyRepository
from app.schemas.prediction import TransactionRequest
from app.services.idempotency_service import IdempotencyService, normalize_key
from app.services.prediction_service import PredictionService


def flagged_payload(**overrides) -> dict:
    payload = {
        "transaction_id": "tx_idem_001",
        "sender_id": "h:sender001",
        "receiver_id": "h:receiver001",
        "sender_balance": 500_000_000,
        "receiver_balance": 200_000,
        "amount": 380_000_000,
        "currency": "VND",
        "timestamp": "2026-05-30T09:14:03+07:00",
        "channel": "TRANSFER",
    }
    payload.update(overrides)
    return payload


def test_repeated_transaction_id_returns_original_prediction_without_duplicate_alert() -> None:
    client = TestClient(app)

    first_response = client.post("/api/v1/predict", json=flagged_payload())
    second_response = client.post("/api/v1/predict", json=flagged_payload())
    assert first_response.status_code == 200
    assert second_response.status_code == 200
    first = first_response.json()
    second = second_response.json()

    assert first == second
    assert len(alert_repository.list()) == 1


def test_idempotency_key_header_overrides_transaction_id() -> None:
    client = TestClient(app)

    first_response = client.post(
        "/api/v1/predict",
        json=flagged_payload(transaction_id="tx_idem_header_001"),
        headers={"Idempotency-Key": "manual-key-001"},
    )
    second_response = client.post(
        "/api/v1/predict",
        json=flagged_payload(transaction_id="tx_idem_header_002"),
        headers={"Idempotency-Key": "manual-key-001"},
    )
    assert first_response.status_code == 200
    assert second_response.status_code == 200
    first = first_response.json()
    second = second_response.json()

    assert first == second
    assert len(alert_repository.list()) == 1


def test_concurrent_same_idempotency_key_creates_single_alert(monkeypatch: pytest.MonkeyPatch) -> None:
    service = PredictionService()
    transaction = TransactionRequest.model_validate(flagged_payload())
    original_create_alert = service.alert_service.create_alert

    def slow_create_alert(*args, **kwargs):
        time.sleep(0.1)
        return original_create_alert(*args, **kwargs)

    monkeypatch.setattr(service.alert_service, "create_alert", slow_create_alert)

    with ThreadPoolExecutor(max_workers=2) as executor:
        responses = list(
            executor.map(
                lambda _: service.predict(transaction, idempotency_key="concurrent-key"),
                range(2),
            )
        )

    assert responses[0] == responses[1]
    assert len(alert_repository.list()) == 1


def test_normalize_key_rejects_empty_key() -> None:
    with pytest.raises(ValueError, match="idempotency key cannot be empty"):
        normalize_key("   ")


def test_get_response_treats_corrupt_payload_as_cache_miss(caplog) -> None:
    repository = InMemoryIdempotencyRepository()
    service = IdempotencyService(repository=repository, ttl_seconds=60)
    repository.set(normalize_key("corrupt-key"), "{not-json", ttl_seconds=60)

    with caplog.at_level(logging.WARNING):
        assert service.get_response("corrupt-key") is None

    assert "predict:corrupt-key" in caplog.text
    assert "{not-json" in caplog.text


def test_claim_response_reclaims_corrupt_payload() -> None:
    repository = InMemoryIdempotencyRepository()
    service = IdempotencyService(repository=repository, ttl_seconds=60)
    normalized_key = normalize_key("corrupt-claim-key")
    repository.set(normalized_key, "{not-json", ttl_seconds=60)

    claim = service.claim_response("corrupt-claim-key")

    assert claim.is_claimed is True
    assert repository.get(normalized_key) == "__processing__"


def test_claim_response_reclaims_corrupt_payload_only_if_value_unchanged() -> None:
    repository = InMemoryIdempotencyRepository()
    service = IdempotencyService(repository=repository, ttl_seconds=60)
    normalized_key = normalize_key("changed-corrupt-claim-key")
    repository.set(normalized_key, "{not-json", ttl_seconds=60)
    repository.set(normalized_key, "claimed-by-other-request", ttl_seconds=60)

    claimed = repository.replace_if_value(
        normalized_key,
        "{not-json",
        "__processing__",
        ttl_seconds=60,
    )

    assert claimed is False
    assert service.repository.get(normalized_key) == "claimed-by-other-request"


def test_idempotency_service_preserves_zero_ttl() -> None:
    repository = InMemoryIdempotencyRepository()
    service = IdempotencyService(repository=repository, ttl_seconds=0)

    assert service.ttl_seconds == 0
