from __future__ import annotations

from dataclasses import dataclass
from math import log1p
from typing import Any

from app.schemas.prediction import TransactionRequest

CTR_THRESHOLD_VND = 400_000_000


@dataclass(frozen=True)
class TransactionFeatures:
    values: dict[str, Any]


class FeatureService:
    def compute(self, transaction: TransactionRequest) -> TransactionFeatures:
        amount = transaction.amount
        sender_balance = transaction.sender_balance
        if sender_balance <= 0:
            amount_to_sender_balance_ratio = 1.0 if amount > 0 else 0.0
        else:
            amount_to_sender_balance_ratio = amount / sender_balance

        near_threshold_lower = CTR_THRESHOLD_VND * 0.90
        is_just_below_threshold = near_threshold_lower <= amount < CTR_THRESHOLD_VND
        # TODO: replace proxy values with historical transaction/Redis rolling aggregate service.
        count_just_below_threshold_24h_proxy = 3 if is_just_below_threshold else 0
        sum_just_below_threshold_24h_proxy = (
            amount * count_just_below_threshold_24h_proxy if is_just_below_threshold else 0.0
        )

        distinct_receivers_1h_proxy = 4 if transaction.channel.value == "TRANSFER" and amount >= 50_000_000 else 1
        sum_amount_1h_proxy = amount * distinct_receivers_1h_proxy if distinct_receivers_1h_proxy > 1 else amount
        rapid_inout_count_1h_proxy = 2 if transaction.channel.value == "TRANSFER" and amount >= 100_000_000 else 0
        chain_depth_proxy = 3 if transaction.channel.value == "TRANSFER" and amount >= 120_000_000 else 1
        velocity_vs_baseline_ratio_proxy = max(1.0, round((amount / max(sender_balance, 1.0)) * 12, 4))
        geo_device_evidence_available = bool(
            transaction.device_id
            or transaction.location_country
            or transaction.location_region
        )
        new_device_proxy = False
        geo_anomaly_proxy = False
        impossible_travel_proxy = False

        values = {
            "amount": amount,
            "sender_balance": sender_balance,
            "receiver_balance": transaction.receiver_balance,
            "amount_to_sender_balance_ratio": amount_to_sender_balance_ratio,
            "channel": transaction.channel.value,
            "currency": transaction.currency,
            "timestamp_hour": transaction.timestamp.hour,
            "is_round_amount": amount > 0 and amount % 1_000_000 == 0,
            "log_amount": round(log1p(amount), 4),
            "amount_to_threshold_ratio": round(amount / CTR_THRESHOLD_VND, 4),
            "count_just_below_threshold_24h_proxy": count_just_below_threshold_24h_proxy,
            "sum_just_below_threshold_24h_proxy": sum_just_below_threshold_24h_proxy,
            "distinct_receivers_1h_proxy": distinct_receivers_1h_proxy,
            "sum_amount_1h_proxy": sum_amount_1h_proxy,
            "rapid_inout_count_1h_proxy": rapid_inout_count_1h_proxy,
            "chain_depth_proxy": chain_depth_proxy,
            "velocity_vs_baseline_ratio_proxy": velocity_vs_baseline_ratio_proxy,
            "geo_device_evidence_available": geo_device_evidence_available,
            "new_device_proxy": new_device_proxy,
            "geo_anomaly_proxy": geo_anomaly_proxy,
            "impossible_travel_proxy": impossible_travel_proxy,
        }
        return TransactionFeatures(values=values)


feature_service = FeatureService()
