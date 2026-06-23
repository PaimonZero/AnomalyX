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

        # Fetch aggregates from RedisAggregateService
        from app.features.redis_aggregates import redis_aggregate_service
        aggs = redis_aggregate_service.get_aggregates(
            sender_id=transaction.sender_id,
            receiver_id=transaction.receiver_id,
            amount=amount,
            timestamp=transaction.timestamp.timestamp(),
            channel=transaction.channel.value,
            device_id=transaction.device_id,
            country=transaction.location_country,
            region=transaction.location_region,
        )

        geo_device_evidence_available = bool(
            transaction.device_id
            or transaction.location_country
            or transaction.location_region
        )

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
            
            # Legacy proxies
            "count_just_below_threshold_24h_proxy": aggs["count_just_below_threshold_24h"],
            "sum_just_below_threshold_24h_proxy": aggs["sum_just_below_threshold_24h"],
            "distinct_receivers_1h_proxy": aggs["distinct_receivers_1h"],
            "sum_amount_1h_proxy": aggs["sum_amount_1h"],
            "rapid_inout_count_1h_proxy": aggs["rapid_inout_count_1h"],
            "chain_depth_proxy": aggs["chain_depth"],
            "velocity_vs_baseline_ratio_proxy": aggs["velocity_vs_baseline_ratio"],
            "geo_device_evidence_available": geo_device_evidence_available,
            "new_device_proxy": aggs["new_device"],
            "geo_anomaly_proxy": aggs["geo_anomaly"],
            "impossible_travel_proxy": aggs["impossible_travel"],

            # Real aggregates (new)
            "has_history": aggs["has_history"],
            "tx_count_1h": aggs["tx_count_1h"],
            "tx_count_24h": aggs["tx_count_24h"],
            "sum_amount_1h": aggs["sum_amount_1h"],
            "sum_amount_24h": aggs["sum_amount_24h"],
            "distinct_receivers_1h": aggs["distinct_receivers_1h"],
            "distinct_receivers_24h": aggs["distinct_receivers_24h"],
            "count_just_below_threshold_24h": aggs["count_just_below_threshold_24h"],
            "sum_just_below_threshold_24h": aggs["sum_just_below_threshold_24h"],
            "rapid_inout_count_1h": aggs["rapid_inout_count_1h"],
            "chain_depth": aggs["chain_depth"],
            "velocity_vs_baseline_ratio": aggs["velocity_vs_baseline_ratio"],
            "new_device": aggs["new_device"],
            "geo_anomaly": aggs["geo_anomaly"],
            "impossible_travel": aggs["impossible_travel"],
        }
        return TransactionFeatures(values=values)



feature_service = FeatureService()
