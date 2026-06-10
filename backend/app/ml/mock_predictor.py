from __future__ import annotations

import hashlib
from math import log1p

from app.features.service import feature_service
from app.ml.predictor import ModelPrediction
from app.schemas.prediction import TopFeature, TransactionChannel, TransactionRequest


class MockModelPredictor:
    model_version = "mock-ml-v1"

    def __init__(self, seed: int = 42) -> None:
        self.seed = seed

    def predict(self, transaction: TransactionRequest) -> ModelPrediction:
        features = feature_service.compute(transaction).values
        amount_component = self._amount_component(transaction.amount)
        balance_component = self._balance_component(
            transaction.amount,
            transaction.sender_balance,
        )
        channel_component = self._channel_component(transaction.channel)
        jitter_component = self._stable_jitter(transaction.transaction_id)

        raw_score = (
            0.42 * amount_component
            + 0.28 * balance_component
            + 0.20 * channel_component
            + 0.10 * jitter_component
        )
        risk_score = round(max(0.0, min(raw_score, 1.0)), 4)

        top_features = [
            TopFeature(
                name="log_amount",
                value=features["log_amount"],
                contribution=round(0.42 * amount_component, 4),
            ),
            TopFeature(
                name="amount_to_sender_balance_ratio",
                value=round(self._safe_ratio(transaction.amount, transaction.sender_balance), 4),
                contribution=round(0.28 * balance_component, 4),
            ),
            TopFeature(
                name="amount_to_threshold_ratio",
                value=features["amount_to_threshold_ratio"],
                contribution=round(0.20 * channel_component, 4),
            ),
        ]

        return ModelPrediction(
            risk_score=risk_score,
            top_features=top_features,
            model_version=self.model_version,
        )

    @staticmethod
    def _amount_component(amount: float) -> float:
        # 400M VND is the large-value reporting threshold used in the TDD.
        return min(log1p(amount) / log1p(400_000_000), 1.0)

    @staticmethod
    def _balance_component(amount: float, sender_balance: float) -> float:
        ratio = MockModelPredictor._safe_ratio(amount, sender_balance)
        return min(ratio, 1.0)

    @staticmethod
    def _channel_component(channel: TransactionChannel) -> float:
        channel_weights = {
            TransactionChannel.CASH_OUT: 0.85,
            TransactionChannel.TRANSFER: 0.70,
            TransactionChannel.CASH_IN: 0.45,
            TransactionChannel.PAYMENT: 0.30,
            TransactionChannel.DEBIT: 0.25,
        }
        return channel_weights[channel]

    @staticmethod
    def _safe_ratio(numerator: float, denominator: float) -> float:
        if denominator <= 0:
            return 1.0 if numerator > 0 else 0.0
        return numerator / denominator

    def _stable_jitter(self, transaction_id: str) -> float:
        digest = hashlib.sha256(f"{self.seed}:{transaction_id}".encode("utf-8")).digest()
        integer_value = int.from_bytes(digest[:8], byteorder="big", signed=False)
        return integer_value / ((1 << 64) - 1)
