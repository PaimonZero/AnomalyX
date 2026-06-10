from fastapi.testclient import TestClient

from app.main import app


def test_health_endpoint_reports_readiness_checks() -> None:
    client = TestClient(app)

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["checks"]["rules_loaded"] is True
    assert body["checks"]["idempotency_configured"] is True
    assert body["storage"]["alert_repository"] in {"in_memory", "supabase"}
    assert body["model"]["mock_enabled"] is True
    assert isinstance(body["metrics_enabled"], bool)
