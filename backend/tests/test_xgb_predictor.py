from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
import pytest

from app.core.config import get_settings
from app.ml.xgb_predictor import XGBPredictor, _compute_features
from app.schemas.prediction import TransactionChannel, TransactionRequest


def make_test_tx(
    amount: float = 100_000.0,
    sender_balance: float = 1_000_000.0,
    receiver_balance: float = 0.0,
    channel: TransactionChannel = TransactionChannel.TRANSFER,
) -> TransactionRequest:
    return TransactionRequest(
        transaction_id="tx_test_123",
        sender_id="sender_1",
        receiver_id="receiver_1",
        amount=amount,
        currency="VND",
        sender_balance=sender_balance,
        receiver_balance=receiver_balance,
        channel=channel,
        timestamp=datetime(2026, 6, 23, 10, 0, 0, tzinfo=timezone.utc),
    )


try:
    import xgboost as xgb
    import shap
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False


def test_feature_mapping_26_columns():
    tx = make_test_tx()
    features = _compute_features(tx)
    
    # Check that feature list matches expected columns
    settings = get_settings()
    import json
    config = json.loads(Path(settings.model_config_path).read_text())
    expected_cols = config["feature_cols"]
    
    # Verify all expected columns are present in features
    for col in expected_cols:
        assert col in features, f"Feature column {col} was not computed."
        
    assert len(expected_cols) == 26  # model_config has 26 columns
    # PaySim columns validation
    assert features["type_encoded"] == 1  # TRANSFER is 1
    assert features["is_transfer_or_cashout"] == 1
    assert features["amount"] == 100_000.0
    assert features["oldbalanceOrg"] == 1_000_000.0
    assert features["newbalanceOrig"] == 900_000.0
    assert features["oldbalanceDest"] == 0.0
    assert features["newbalanceDest"] == 100_000.0


@pytest.mark.skipif(not XGBOOST_AVAILABLE, reason="xgboost and shap not available in test environment")
def test_prediction_contract():
    settings = get_settings()
    
    # If the real model artifact files exist, run the test on the real model
    if Path(settings.model_path).is_file() and Path(settings.model_config_path).is_file():
        predictor = XGBPredictor(
            model_path=settings.model_path,
            config_path=settings.model_config_path,
        )

        tx = make_test_tx()
        prediction = predictor.predict(tx)
        
        assert prediction.risk_score >= 0.0 and prediction.risk_score <= 1.0
        assert prediction.model_version == predictor.model_version
        assert isinstance(prediction.top_features, list)
    else:
        pytest.skip("Real model artifacts not available for this test.")


@pytest.mark.skipif(not XGBOOST_AVAILABLE, reason="xgboost and shap not available in test environment")
def test_shap_fallback_on_error(monkeypatch: pytest.MonkeyPatch):
    settings = get_settings()

    
    if Path(settings.model_path).is_file() and Path(settings.model_config_path).is_file():
        predictor = XGBPredictor(
            model_path=settings.model_path,
            config_path=settings.model_config_path,
        )
        
        # Force SHAP explainer to fail
        def mock_shap_explainer(*args, **kwargs):
            raise RuntimeError("SHAP failed")
            
        monkeypatch.setattr("shap.TreeExplainer", mock_shap_explainer)
        # Clear cached explainer
        predictor._shap_explainer = None
        
        tx = make_test_tx()
        prediction = predictor.predict(tx)
        
        # Verify prediction still succeeds but with empty top_features
        assert prediction.risk_score >= 0.0 and prediction.risk_score <= 1.0
        assert prediction.top_features == []
    else:
        pytest.skip("Real model artifacts not available for this test.")
