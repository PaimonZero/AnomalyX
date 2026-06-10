from fastapi.testclient import TestClient

from app.api.dependencies import auth as auth_dependency
from app.main import app


def valid_payload(**overrides) -> dict:
    payload = {
        "transaction_id": "tx_contract_001",
        "sender_id": "h:sender001",
        "receiver_id": "h:receiver001",
        "sender_balance": 15_000_000,
        "receiver_balance": 200_000,
        "amount": 9_500_000,
        "currency": "VND",
        "timestamp": "2026-05-30T09:14:03+07:00",
        "channel": "TRANSFER",
    }
    payload.update(overrides)
    return payload


def test_protected_endpoint_rejects_missing_bearer_token() -> None:
    original_override = app.dependency_overrides.pop(auth_dependency.require_api_auth, None)
    client = TestClient(app)

    try:
        response = client.post("/api/v1/predict", json=valid_payload())
    finally:
        if original_override is not None:
            app.dependency_overrides[auth_dependency.require_api_auth] = original_override

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "unauthorized"


# Restore test auth override for subsequent tests in this module.
app.dependency_overrides[auth_dependency.require_api_auth] = lambda: "test_key"




def test_batch_score_returns_flagged_subset() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/v1/batch-score",
        json={
            "batch_id": "batch_001",
            "transactions": [
                valid_payload(transaction_id="tx_batch_low_001", amount=100_000),
                valid_payload(
                    transaction_id="tx_batch_high_001",
                    amount=380_000_000,
                    sender_balance=500_000_000,
                ),
            ],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["batch_id"] == "batch_001"
    assert body["total_transactions"] == 2
    assert body["flagged_count"] == 1
    assert len(body["predictions"]) == 2
    assert len(body["flagged_predictions"]) == 1
    assert body["flagged_predictions"][0]["transaction_id"] == "tx_batch_high_001"
    assert body["alert_ids"]
