from fastapi.testclient import TestClient

from app.main import app


def test_metrics_endpoint_returns_prometheus_text() -> None:
    client = TestClient(app)

    response = client.get("/api/v1/metrics")

    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    assert "anomalyx_http_requests_total" in response.text


def test_request_metrics_are_recorded_after_health_call() -> None:
    client = TestClient(app)

    client.get("/api/v1/health")
    response = client.get("/api/v1/metrics")

    assert 'path="/api/v1/health"' in response.text


def test_metrics_include_alert_llm_and_drift_placeholders() -> None:
    client = TestClient(app)

    response = client.get("/api/v1/metrics")

    assert response.status_code == 200
    assert "anomalyx_alerts_total" in response.text
    assert "anomalyx_llm_fallback_total" in response.text
    assert "anomalyx_model_drift_placeholder" in response.text
