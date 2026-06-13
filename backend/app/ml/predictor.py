from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from app.schemas.prediction import TopFeature, TransactionRequest


@dataclass(frozen=True)
class ModelPrediction:
    risk_score: float
    top_features: list[TopFeature]
    model_version: str


class ModelPredictor(Protocol):
    model_version: str

    def predict(self, transaction: TransactionRequest) -> ModelPrediction:
        """Return a risk score and top features for a transaction."""
