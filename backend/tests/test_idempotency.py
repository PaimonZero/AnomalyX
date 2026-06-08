from fastapi.testclient import TestClient

from app.main import app
from app.repositories.alert_repository import alert_repository


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

    first = client.post("/api/v1/predict", json=flagged_payload()).json()
    second = client.post("/api/v1/predict", json=flagged_payload()).json()

    assert first == second
    assert len(alert_repository.list()) == 1


def test_idempotency_key_header_overrides_transaction_id() -> None:
    client = TestClient(app)

    first = client.post(
        "/api/v1/predict",
        json=flagged_payload(transaction_id="tx_idem_header_001"),
        headers={"Idempotency-Key": "manual-key-001"},
    ).json()
    second = client.post(
        "/api/v1/predict",
        json=flagged_payload(transaction_id="tx_idem_header_002"),
        headers={"Idempotency-Key": "manual-key-001"},
    ).json()

    assert first == second
    assert len(alert_repository.list()) == 1
