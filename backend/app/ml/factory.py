from __future__ import annotations

from app.core.config import get_settings
from app.ml.mock_predictor import MockModelPredictor
from app.ml.predictor import ModelPredictor


def get_model_predictor() -> ModelPredictor:
    settings = get_settings()
    if settings.mock_ml_enabled:
        return MockModelPredictor(seed=settings.mock_ml_seed)

    raise NotImplementedError("Real ML predictor is not implemented yet.")
