from fastapi.testclient import TestClient

from app.main import app
from app.repositories.alert_repository import alert_repository


def flagged_payload(**overrides) -> dict:
    payload = {
        "transaction_id": "tx_alert_001",
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


def test_flagged_prediction_creates_alert() -> None:
    alert_repository.clear()
    client = TestClient(app)

    prediction_response = client.post("/api/v1/predict", json=flagged_payload())

    assert prediction_response.status_code == 200
    prediction = prediction_response.json()
    assert prediction["is_flagged"] is True
    assert prediction["alert_id"] is not None

    alert_response = client.get(f"/api/v1/alerts/{prediction['alert_id']}")

    assert alert_response.status_code == 200
    alert = alert_response.json()
    assert alert["id"] == prediction["alert_id"]
    assert alert["transaction_id"] == "tx_alert_001"
    assert alert["status"] == "NEW"
    assert alert["risk_level"] == "HIGH"


def test_list_and_filter_alerts() -> None:
    alert_repository.clear()
    client = TestClient(app)

    client.post("/api/v1/predict", json=flagged_payload(transaction_id="tx_alert_002"))

    all_alerts = client.get("/api/v1/alerts")
    open_alerts = client.get("/api/v1/alerts", params={"status": "NEW"})
    dismissed_alerts = client.get("/api/v1/alerts", params={"status": "DISMISSED"})

    assert all_alerts.status_code == 200
    assert len(all_alerts.json()) == 1
    assert len(open_alerts.json()) == 1
    assert dismissed_alerts.json() == []


def test_update_alert_status() -> None:
    alert_repository.clear()
    client = TestClient(app)
    prediction = client.post(
        "/api/v1/predict",
        json=flagged_payload(transaction_id="tx_alert_003"),
    ).json()

    response = client.patch(
        f"/api/v1/alerts/{prediction['alert_id']}/status",
        json={"status": "ESCALATED"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "ESCALATED"


def test_unknown_alert_returns_404() -> None:
    alert_repository.clear()
    client = TestClient(app)

    response = client.get("/api/v1/alerts/al_missing")

    assert response.status_code == 404
