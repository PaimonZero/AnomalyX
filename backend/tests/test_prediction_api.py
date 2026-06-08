from fastapi.testclient import TestClient

from app.main import app


def valid_payload(**overrides) -> dict:
    payload = {
        "transaction_id": "tx_predict_001",
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


def test_predict_returns_mock_ml_decision_response() -> None:
    client = TestClient(app)

    response = client.post("/api/v1/predict", json=valid_payload())

    assert response.status_code == 200
    body = response.json()
    assert body["transaction_id"] == "tx_predict_001"
    assert 0 <= body["risk_score"] <= 1
    assert body["risk_level"] in {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
    assert isinstance(body["is_flagged"], bool)
    assert body["model_version"] == "mock-ml-v1"
    assert body["top_features"]
    assert body["explanation"] is None
    assert body["alert_id"] is None


def test_predict_includes_triggered_rules() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/v1/predict",
        json=valid_payload(
            transaction_id="tx_predict_rule_001",
            amount=380_000_000,
            sender_balance=500_000_000,
            channel="TRANSFER",
        ),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["risk_level"] == "HIGH"
    assert body["is_flagged"] is True
    assert any(rule["id"] == "R-THRESHOLD-01" for rule in body["triggered_rules"])


def test_predict_rejects_invalid_payload() -> None:
    client = TestClient(app)
    payload = valid_payload(amount=-1)

    response = client.post("/api/v1/predict", json=payload)

    assert response.status_code == 422
