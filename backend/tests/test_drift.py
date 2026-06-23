from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.core.drift import ScoreDriftDetector, score_drift_detector
from app.core.metrics import MODEL_DRIFT_PSI
from app.main import app


@pytest.fixture(autouse=True)
def reset_detector():
    # Store old state
    old_window = score_drift_detector.window_size
    old_recent = list(score_drift_detector.recent_scores)
    old_baseline = list(score_drift_detector.baseline_scores)
    
    # Reset to default
    score_drift_detector.recent_scores.clear()
    score_drift_detector.window_size = 1000
    score_drift_detector.baseline_scores = (
        [0.05] * 800 + [0.2] * 150 + [0.55] * 30 + [0.85] * 20
    )
    score_drift_detector._cached_baseline_pcts = score_drift_detector._compute_pcts(
        score_drift_detector.baseline_scores
    )
    MODEL_DRIFT_PSI.set(0.0)
    
    yield
    
    # Restore
    score_drift_detector.window_size = old_window
    score_drift_detector.recent_scores.clear()
    score_drift_detector.recent_scores.extend(old_recent)
    score_drift_detector.set_baseline(old_baseline)


def test_record_score_accumulates():
    detector = ScoreDriftDetector(window_size=5)
    
    # Record scores
    detector.record_score(0.1)
    detector.record_score(0.2)
    
    assert len(detector.recent_scores) == 2
    assert list(detector.recent_scores) == [0.1, 0.2]
    
    # Exceed window size
    detector.record_score(0.3)
    detector.record_score(0.4)
    detector.record_score(0.5)
    detector.record_score(0.6)
    
    assert len(detector.recent_scores) == 5
    assert list(detector.recent_scores) == [0.2, 0.3, 0.4, 0.5, 0.6]


def test_psi_zero_identical_distributions():
    detector = ScoreDriftDetector(window_size=100)
    
    # Baseline has 80% low, 15% medium-low, 3% medium-high, 2% high
    # Let's set a baseline and feed identical distribution to recent
    baseline = [0.05] * 80 + [0.2] * 15 + [0.5] * 3 + [0.9] * 2
    detector.set_baseline(baseline)
    
    for s in baseline:
        detector.record_score(s)
        
    psi = detector.compute_psi()
    # Identical distributions should have PSI close to 0 (very small due to floating point and bin edges)
    assert psi < 0.05


def test_psi_high_shifted_distribution():
    detector = ScoreDriftDetector(window_size=100)
    
    # Baseline has mostly low risk (80% 0.05, etc.)
    baseline = [0.05] * 80 + [0.2] * 15 + [0.55] * 3 + [0.85] * 2
    detector.set_baseline(baseline)
    
    # Shifted: feed mostly high risk scores (e.g. 80% high risk)
    shifted = [0.85] * 80 + [0.55] * 15 + [0.2] * 3 + [0.05] * 2
    for s in shifted:
        detector.record_score(s)
        
    psi = detector.compute_psi()
    # Shifting distribution dramatically should result in a high PSI (> 0.2)
    assert psi > 1.0


def test_api_endpoints():
    client = TestClient(app)
    
    # 1. Update baseline via API
    baseline_payload = {"scores": [0.05] * 80 + [0.2] * 20}
    response = client.post(
        "/api/v1/drift/baseline",
        json=baseline_payload,
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    
    # 2. Get status API
    response = client.get("/api/v1/drift/status")
    assert response.status_code == 200
    data = response.json()
    assert "psi" in data
    assert data["baseline_scores_count"] == 100
    assert data["drift_status"] in ("NO_DRIFT", "WARNING", "DRIFT")


def test_drift_gauge_updated_in_predict_flow(monkeypatch: pytest.MonkeyPatch):
    client = TestClient(app)
    
    # Configure drift detector to compute PSI after just 2 scores (window size = 2)
    monkeypatch.setattr(score_drift_detector, "window_size", 2)
    score_drift_detector.recent_scores.clear()
    
    # Set a tiny baseline
    score_drift_detector.set_baseline([0.05, 0.05, 0.05, 0.05, 0.05])
    
    # Trigger 2 predictions with high scores to cause drift calculation
    tx_payload = {
        "transaction_id": "tx_drift_1",
        "sender_id": "sender_drift",
        "receiver_id": "rec_drift",
        "amount": 500_000.0,
        "currency": "VND",
        "sender_balance": 10_000_000.0,
        "receiver_balance": 10_000_000.0,
        "channel": "TRANSFER",
        "timestamp": "2026-06-23T08:00:00Z",
    }
    
    # We will mock XGBPredictor so it returns high risk score 0.95
    # (or let the mock predictor handle it if MOCK_ML_ENABLED is true)
    # The default mock predictor returns a score based on rules/random, let's just mock the predictor class return
    class MockPrediction:
        risk_score = 0.95
        top_features = []
        model_version = "mock-ml-v1"
        
    class MockPredictor:
        def predict(self, *args, **kwargs):
            return MockPrediction()
            
    monkeypatch.setattr("app.services.prediction_service.get_model_predictor", lambda: MockPredictor())
    
    # Run first prediction
    res1 = client.post("/api/v1/predict", json=tx_payload)
    assert res1.status_code == 200
    
    # Run second prediction (different ID)
    tx_payload["transaction_id"] = "tx_drift_2"
    res2 = client.post("/api/v1/predict", json=tx_payload)
    assert res2.status_code == 200
    
    # PSI should have been calculated and gauge updated
    assert len(score_drift_detector.recent_scores) == 2
    psi = score_drift_detector.compute_psi()
    assert psi > 0.0
    
    # Verify metric gauge matches computed PSI by querying the metrics endpoint
    metrics_res = client.get("/api/v1/metrics")
    assert metrics_res.status_code == 200
    assert f"anomalyx_model_drift_psi {psi}" in metrics_res.text

