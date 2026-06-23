from __future__ import annotations

import json
import logging
import math
from pathlib import Path
from typing import Any

import numpy as np

_logger = logging.getLogger(__name__)

from app.ml.predictor import ModelPrediction
from app.schemas.prediction import TopFeature, TransactionChannel, TransactionRequest

_CHANNEL_ENCODING: dict[TransactionChannel, int] = {
    TransactionChannel.PAYMENT: 0,
    TransactionChannel.TRANSFER: 1,
    TransactionChannel.CASH_OUT: 2,
    TransactionChannel.DEBIT: 3,
    TransactionChannel.CASH_IN: 4,
}

# PaySim training threshold for flag_near_threshold / flag_large_tx.
# This is a PaySim dataset artifact (~200 K synthetic USD-like units), NOT a VND business
# threshold. The rule engine uses CTR_THRESHOLD_VND=400_000_000 for Vietnamese Dong.
# If the model is retrained on VND data this constant must be updated to match.
_PAYSIM_THRESHOLD = 200_000.0


def _compute_features(tx: TransactionRequest) -> dict[str, Any]:
    amount = tx.amount
    old_bal_orig = tx.sender_balance
    old_bal_dest = tx.receiver_balance
    new_bal_orig = max(0.0, old_bal_orig - amount)
    new_bal_dest = old_bal_dest + amount

    eps = 1.0
    # balance_diff_orig is non-zero only when sender is over-drafted (amount > old_bal_orig).
    # balance_diff_dest is always 0 when new_bal_dest is computed from the same request fields;
    # in the original PaySim dataset these caught reporting inconsistencies in raw CSV records.
    balance_diff_orig = abs(old_bal_orig - new_bal_orig - amount)
    balance_diff_dest = abs(old_bal_dest + amount - new_bal_dest)

    # Fetch aggregates from RedisAggregateService
    from app.features.redis_aggregates import redis_aggregate_service
    aggs = redis_aggregate_service.get_aggregates(
        sender_id=tx.sender_id,
        receiver_id=tx.receiver_id,
        amount=amount,
        timestamp=tx.timestamp.timestamp(),
        channel=tx.channel.value,
        device_id=tx.device_id,
        country=tx.location_country,
        region=tx.location_region,
    )

    # Thresholds for flag features
    VELOCITY_THRESHOLD = 5
    FANOUT_THRESHOLD = 3

    flag_high_velocity = int(aggs["tx_count_sender"] >= VELOCITY_THRESHOLD)
    flag_high_fanout = int(aggs["fan_out_orig"] >= FANOUT_THRESHOLD)

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
        # Real historical/velocity features
        "tx_count_sender": aggs["tx_count_sender"],
        "total_amount_sender": aggs["total_amount_sender"],
        "avg_amount_sender": aggs["avg_amount_sender"],
        "amount_vs_avg": aggs["amount_vs_avg"],
        "unique_dest_sender": aggs["unique_dest_sender"],
        "fan_out_orig": aggs["fan_out_orig"],
        "fan_in_dest": aggs["fan_in_dest"],
        # AML flags
        "flag_near_threshold": int(_PAYSIM_THRESHOLD * 0.9 <= amount < _PAYSIM_THRESHOLD),
        "flag_large_tx": int(amount >= _PAYSIM_THRESHOLD),
        "flag_high_velocity": flag_high_velocity,
        "flag_high_fanout": flag_high_fanout,
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
        self._shap_explainer = None

    def predict(self, transaction: TransactionRequest) -> ModelPrediction:
        features = _compute_features(transaction)
        X = np.array([[features[c] for c in self.feature_cols]], dtype=np.float32)

        risk_score = float(self._model.predict_proba(X)[0, 1])

        top_features = self._shap_top_features(X, features)

        return ModelPrediction(
            risk_score=risk_score,
            top_features=top_features,
            model_version=self.model_version,
        )

    def _shap_top_features(
        self, X: np.ndarray, features: dict[str, Any], k: int = 5
    ) -> list[TopFeature]:
        try:
            import shap  # optional at runtime

            if self._shap_explainer is None:
                self._shap_explainer = shap.TreeExplainer(self._model)
            shap_vals = self._shap_explainer.shap_values(X)[0]
            ranked = sorted(
                zip(self.feature_cols, shap_vals, strict=True),
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
            _logger.warning("SHAP explanation failed; returning empty top_features", exc_info=True)
            return []
