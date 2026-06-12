from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np

from app.ml.predictor import ModelPrediction
from app.schemas.prediction import TopFeature, TransactionChannel, TransactionRequest

_CHANNEL_ENCODING: dict[TransactionChannel, int] = {
    TransactionChannel.PAYMENT: 0,
    TransactionChannel.TRANSFER: 1,
    TransactionChannel.CASH_OUT: 2,
    TransactionChannel.DEBIT: 3,
    TransactionChannel.CASH_IN: 4,
}

# PaySim training threshold used for flag_near_threshold / flag_large_tx features.
_PAYSIM_THRESHOLD = 200_000.0


def _compute_features(tx: TransactionRequest, feature_cols: list[str]) -> dict[str, Any]:
    amount = tx.amount
    old_bal_orig = tx.sender_balance
    old_bal_dest = tx.receiver_balance
    new_bal_orig = max(0.0, old_bal_orig - amount)
    new_bal_dest = old_bal_dest + amount

    eps = 1.0
    balance_diff_orig = abs(old_bal_orig - new_bal_orig - amount)
    balance_diff_dest = abs(old_bal_dest + amount - new_bal_dest)

    raw: dict[str, Any] = {
        "type_encoded": _CHANNEL_ENCODING[tx.channel],
        "is_transfer_or_cashout": int(
            tx.channel in (TransactionChannel.TRANSFER, TransactionChannel.CASH_OUT)
        ),
        "log_amount": math.log1p(amount),
        "amount": amount,
        "oldbalanceOrg": old_bal_orig,
        "newbalanceOrig": new_bal_orig,
        "oldbalanceDest": old_bal_dest,
        "newbalanceDest": new_bal_dest,
        "balance_diff_orig": balance_diff_orig,
        "balance_diff_dest": balance_diff_dest,
        "balance_drain_orig": int(new_bal_orig == 0.0),
        "amount_to_balance_ratio": amount / (old_bal_orig + eps),
        "dest_balance_change_ratio": (new_bal_dest - old_bal_dest) / (amount + eps),
        # step: PaySim time-step proxy — use hour-of-day (0-23)
        "step": tx.timestamp.hour,
        # Historical/velocity features — cold-start defaults (no Redis history)
        "tx_count_sender": 1,
        "total_amount_sender": amount,
        "avg_amount_sender": amount,
        "amount_vs_avg": 1.0,
        "unique_dest_sender": 1,
        "fan_out_orig": 1,
        "fan_in_dest": 0,
        # AML flags
        "flag_near_threshold": int(_PAYSIM_THRESHOLD * 0.9 <= amount < _PAYSIM_THRESHOLD),
        "flag_large_tx": int(amount >= _PAYSIM_THRESHOLD),
        "flag_high_velocity": 0,
        "flag_high_fanout": 0,
        "flag_balance_inconsist": int(balance_diff_orig > 1 or balance_diff_dest > 1),
    }
    return raw


class XGBPredictor:
    """Real XGBoost predictor backed by a trained model artifact."""

    def __init__(self, model_path: str, config_path: str) -> None:
        import xgboost as xgb  # lazy import — not installed in test environments

        config = json.loads(Path(config_path).read_text())
        self.feature_cols: list[str] = config["feature_cols"]
        self.model_version: str = config["model_version"]

        self._model = xgb.XGBClassifier()
        self._model.load_model(model_path)

    def predict(self, transaction: TransactionRequest) -> ModelPrediction:
        features = _compute_features(transaction, self.feature_cols)
        X = np.array([[features[c] for c in self.feature_cols]], dtype=np.float32)

        risk_score = float(self._model.predict_proba(X)[0, 1])

        top_features = self._shap_top_features(X, features)

        return ModelPrediction(
            risk_score=round(risk_score, 4),
            top_features=top_features,
            model_version=self.model_version,
        )

    def _shap_top_features(
        self, X: np.ndarray, features: dict[str, Any], k: int = 5
    ) -> list[TopFeature]:
        try:
            import shap  # optional at runtime

            explainer = shap.TreeExplainer(self._model)
            shap_vals = explainer.shap_values(X)[0]
            ranked = sorted(
                zip(self.feature_cols, shap_vals),
                key=lambda pair: abs(pair[1]),
                reverse=True,
            )[:k]
            return [
                TopFeature(
                    name=name,
                    value=round(float(features[name]), 4),
                    contribution=round(float(val), 4),
                )
                for name, val in ranked
            ]
        except Exception:
            return []
