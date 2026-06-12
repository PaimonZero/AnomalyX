from __future__ import annotations

from functools import lru_cache

from app.core.config import get_settings
from app.ml.mock_predictor import MockModelPredictor
from app.ml.predictor import ModelPredictor


@lru_cache(maxsize=1)
def get_model_predictor() -> ModelPredictor:
    settings = get_settings()
    if settings.mock_ml_enabled:
        return MockModelPredictor(seed=settings.mock_ml_seed)

    from app.ml.xgb_predictor import XGBPredictor

    return XGBPredictor(
        model_path=settings.model_path,
        config_path=settings.model_config_path,
    )
