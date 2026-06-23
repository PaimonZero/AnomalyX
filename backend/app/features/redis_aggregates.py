from __future__ import annotations

import json
import logging
from collections import Counter, defaultdict
from datetime import datetime
from typing import Any

from redis import Redis
from app.core.config import get_settings

_logger = logging.getLogger(__name__)


class RedisAggregateService:
    def __init__(self, redis_url: str | None = None) -> None:
        settings = get_settings()
        self.idempotency_store = settings.idempotency_store
        self.use_redis = self.idempotency_store == "redis"
        self.client = None

        if self.use_redis:
            try:
                self.client = Redis.from_url(
                    redis_url or settings.redis_url,
                    decode_responses=True,
                    socket_connect_timeout=settings.redis_socket_connect_timeout_seconds,
                    socket_timeout=settings.redis_socket_timeout_seconds,
                )
                # Test connection
                self.client.ping()
                _logger.info("RedisAggregateService successfully connected to Redis.")
            except Exception as e:
                _logger.warning(
                    f"Redis connection failed for aggregates, falling back to in-memory: {e}"
                )
                self.use_redis = False

        if not self.use_redis:
            # In-memory storage structures for fallback/testing
            self._sent_txs = defaultdict(list)  # sender_id -> list of dicts
            self._received_txs = defaultdict(list)  # receiver_id -> list of dicts
            self._chain_depths = defaultdict(lambda: 1)  # account_id -> int

    def clear(self) -> None:
        if self.use_redis and self.client:
            try:
                keys = self.client.keys("anomalyx:agg:*")
                if keys:
                    self.client.delete(*keys)
            except Exception as e:
                _logger.warning(f"Failed to clear Redis keys in clear(): {e}")
        # Always clear in-memory maps
        if hasattr(self, "_sent_txs"):
            self._sent_txs.clear()
            self._received_txs.clear()
            self._chain_depths.clear()


    def _get_sent_key(self, sender_id: str) -> str:
        return f"anomalyx:agg:{sender_id}:sent"

    def _get_received_key(self, receiver_id: str) -> str:
        return f"anomalyx:agg:{receiver_id}:received"

    def _get_chain_depth_key(self, account_id: str) -> str:
        return f"anomalyx:agg:{account_id}:chain_depth"

    def record_transaction(
        self,
        tx_id: str,
        sender_id: str,
        receiver_id: str,
        amount: float,
        timestamp: float,
        channel: str,
        device_id: str | None = None,
        country: str | None = None,
        region: str | None = None,
    ) -> None:
        tx_data = {
            "tx_id": tx_id,
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "amount": amount,
            "timestamp": timestamp,
            "channel": channel,
            "device_id": device_id,
            "country": country,
            "region": region,
        }
        serialized = json.dumps(tx_data)

        if self.use_redis and self.client:
            try:
                # Prune older than 24h
                cutoff = timestamp - 86400
                sent_key = self._get_sent_key(sender_id)
                received_key = self._get_received_key(receiver_id)

                self.client.zremrangebyscore(sent_key, "-inf", f"({cutoff}")
                self.client.zremrangebyscore(received_key, "-inf", f"({cutoff}")

                # Record transaction
                self.client.zadd(sent_key, {serialized: timestamp})
                self.client.zadd(received_key, {serialized: timestamp})

                # Set expiry on keys (e.g., 25 hours to ensure they clean up if inactive)
                self.client.expire(sent_key, 90000)
                self.client.expire(received_key, 90000)

                # Chain depth update (TRANSFER only propagates depth)
                if channel == "TRANSFER":
                    sender_depth_key = self._get_chain_depth_key(sender_id)
                    receiver_depth_key = self._get_chain_depth_key(receiver_id)
                    sender_depth = self.client.get(sender_depth_key)
                    depth = int(sender_depth) if sender_depth else 1
                    self.client.setex(receiver_depth_key, 3600, str(depth + 1))

            except Exception as e:
                _logger.error(f"Error recording transaction in Redis: {e}", exc_info=True)
        else:
            # In-memory path
            cutoff = timestamp - 86400
            # Prune and insert
            self._sent_txs[sender_id] = [
                t for t in self._sent_txs[sender_id] if t["timestamp"] >= cutoff
            ]
            self._received_txs[receiver_id] = [
                t for t in self._received_txs[receiver_id] if t["timestamp"] >= cutoff
            ]

            self._sent_txs[sender_id].append(tx_data)
            self._received_txs[receiver_id].append(tx_data)

            if channel == "TRANSFER":
                sender_depth = self._chain_depths[sender_id]
                self._chain_depths[receiver_id] = sender_depth + 1

    def get_aggregates(
        self,
        sender_id: str,
        receiver_id: str,
        amount: float,
        timestamp: float,
        channel: str,
        device_id: str | None = None,
        country: str | None = None,
        region: str | None = None,
    ) -> dict[str, Any]:
        # Current tx details (to be included in counts/sums)
        current_tx = {
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "amount": amount,
            "timestamp": timestamp,
            "channel": channel,
            "device_id": device_id,
            "country": country,
            "region": region,
        }

        # Fetch history (last 24 hours relative to current transaction timestamp)
        cutoff_24h = timestamp - 86400
        cutoff_1h = timestamp - 3600

        history_sent = []
        history_received = []

        if self.use_redis and self.client:
            try:
                sent_key = self._get_sent_key(sender_id)
                received_key = self._get_received_key(receiver_id)

                # Prune older than 24h
                self.client.zremrangebyscore(sent_key, "-inf", f"({cutoff_24h}")
                self.client.zremrangebyscore(received_key, "-inf", f"({cutoff_24h}")

                # Fetch all remaining ZSET elements (which are in the last 24h window)
                raw_sent = self.client.zrange(sent_key, 0, -1)
                raw_received = self.client.zrange(received_key, 0, -1)

                for item in raw_sent:
                    try:
                        history_sent.append(json.loads(item))
                    except Exception:
                        pass
                for item in raw_received:
                    try:
                        history_received.append(json.loads(item))
                    except Exception:
                        pass
            except Exception as e:
                _logger.error(f"Error fetching history from Redis: {e}", exc_info=True)
        else:
            # In-memory path
            history_sent = [
                t for t in self._sent_txs[sender_id] if t["timestamp"] >= cutoff_24h
            ]
            history_received = [
                t for t in self._received_txs[receiver_id] if t["timestamp"] >= cutoff_24h
            ]

        # Filter history strictly prior to current transaction timestamp to compute historical features
        # (This is for cold-start indicators like new_device, geo_anomaly, etc.)
        history_sent_prior = [t for t in history_sent if t["timestamp"] < timestamp]

        # Combine history + current transaction for predictive features
        all_sent = history_sent_prior + [current_tx]

        # 1. Has history indicator (based on history prior to this transaction)
        has_history = len(history_sent_prior) > 0

        # 2. Sent counts and sums in windows
        tx_count_1h = sum(1 for t in all_sent if t["timestamp"] >= cutoff_1h)
        tx_count_24h = len(all_sent)

        sum_amount_1h = sum(t["amount"] for t in all_sent if t["timestamp"] >= cutoff_1h)
        sum_amount_24h = sum(t["amount"] for t in all_sent)

        # 3. Unique destinations
        distinct_receivers_1h = len(
            {t["receiver_id"] for t in all_sent if t["timestamp"] >= cutoff_1h}
        )
        distinct_receivers_24h = len({t["receiver_id"] for t in all_sent})

        # 4. Count and sum just below threshold 400M VND (360M <= amount < 400M)
        just_below_txs = [
            t
            for t in all_sent
            if 360_000_000 <= t["amount"] < 400_000_000
        ]
        count_just_below_threshold_24h = len(just_below_txs)
        sum_just_below_threshold_24h = sum(t["amount"] for t in just_below_txs)

        # 5. Rapid in-out pattern count (within 1 hour)
        # For each outflow (TRANSFER/CASH_OUT) sent by sender in last 1 hour,
        # did they receive any inflow (TRANSFER/CASH_IN) in the 1 hour before that outflow?
        # Note: we need the sender's received history.
        # Let's get the sender's received history in the last 2 hours.
        sender_received_history = []
        if self.use_redis and self.client:
            try:
                sender_received_key = self._get_received_key(sender_id)
                self.client.zremrangebyscore(sender_received_key, "-inf", f"({timestamp - 7200}")
                raw_received = self.client.zrange(sender_received_key, 0, -1)
                for item in raw_received:
                    try:
                        sender_received_history.append(json.loads(item))
                    except Exception:
                        pass
            except Exception:
                pass
        else:
            sender_received_history = [
                t for t in self._received_txs[sender_id] if t["timestamp"] >= timestamp - 7200
            ]

        # Calculate rapid inouts:
        rapid_inout_count_1h = 0
        outflows_1h = [
            t
            for t in all_sent
            if t["timestamp"] >= cutoff_1h
            and t["channel"] in ("TRANSFER", "CASH_OUT")
        ]
        for out_tx in outflows_1h:
            t_out = out_tx["timestamp"]
            # Look for any received inflow (CASH_IN or TRANSFER) in [t_out - 3600, t_out]
            has_preceding_inflow = any(
                in_tx["timestamp"] <= t_out
                and t_out - in_tx["timestamp"] <= 3600
                and in_tx["channel"] in ("TRANSFER", "CASH_IN")
                for in_tx in sender_received_history
            )
            if has_preceding_inflow:
                rapid_inout_count_1h += 1

        # 6. Chain depth
        chain_depth = 1
        if self.use_redis and self.client:
            try:
                val = self.client.get(self._get_chain_depth_key(sender_id))
                if val:
                    chain_depth = int(val)
            except Exception:
                pass
        else:
            chain_depth = self._chain_depths[sender_id]

        # 7. ML predictor stats (incorporating current transaction)
        # Average amount sender
        avg_amount_sender = sum_amount_24h / tx_count_24h
        # Amount vs average of history (excluding current tx, fallback to 1.0 if no history)
        avg_amount_history = 0.0
        history_sent_24h = [t for t in history_sent_prior if t["timestamp"] >= cutoff_24h]
        if history_sent_24h:
            avg_amount_history = sum(t["amount"] for t in history_sent_24h) / len(history_sent_24h)
        amount_vs_avg = amount / (avg_amount_history + 1.0) if history_sent_24h else 1.0

        # Unique dest sender (same as distinct_receivers_24h)
        unique_dest_sender = distinct_receivers_24h
        fan_out_orig = distinct_receivers_24h

        # Fan-in of destination: unique senders sending to receiver_id in the last 24h
        # Combined history received + current transaction
        all_received = [t for t in history_received if t["timestamp"] < timestamp] + [current_tx]
        fan_in_dest = len({t["sender_id"] for t in all_received})

        # 8. Geo/Device flags (prior to current transaction)
        geo_dev = self.get_geo_device_features(
            sender_id=sender_id,
            device_id=device_id,
            country=country,
            region=region,
            timestamp=timestamp,
        )
        new_device = geo_dev["new_device"]
        geo_anomaly = geo_dev["geo_anomaly"]
        impossible_travel = geo_dev["impossible_travel"]

        # 9. Velocity vs Baseline ratio
        # Ratio of current transaction amount to the average amount from history
        velocity_vs_baseline_ratio = 1.0
        if avg_amount_history > 0:
            velocity_vs_baseline_ratio = amount / avg_amount_history
        velocity_vs_baseline_ratio = max(1.0, round(velocity_vs_baseline_ratio, 4))

        return {
            "has_history": has_history,
            "tx_count_1h": tx_count_1h,
            "tx_count_24h": tx_count_24h,
            "sum_amount_1h": sum_amount_1h,
            "sum_amount_24h": sum_amount_24h,
            "distinct_receivers_1h": distinct_receivers_1h,
            "distinct_receivers_24h": distinct_receivers_24h,
            "count_just_below_threshold_24h": count_just_below_threshold_24h,
            "sum_just_below_threshold_24h": sum_just_below_threshold_24h,
            "rapid_inout_count_1h": rapid_inout_count_1h,
            "chain_depth": chain_depth,
            "tx_count_sender": tx_count_24h,
            "total_amount_sender": sum_amount_24h,
            "avg_amount_sender": avg_amount_sender,
            "amount_vs_avg": amount_vs_avg,
            "unique_dest_sender": unique_dest_sender,
            "fan_out_orig": fan_out_orig,
            "fan_in_dest": fan_in_dest,
            "new_device": new_device,
            "geo_anomaly": geo_anomaly,
            "impossible_travel": impossible_travel,
            "velocity_vs_baseline_ratio": velocity_vs_baseline_ratio,
        }

    def get_geo_device_features(
        self,
        sender_id: str,
        device_id: str | None,
        country: str | None,
        region: str | None,
        timestamp: float,
    ) -> dict[str, bool]:
        # Fetch sender's history prior to the current timestamp
        cutoff_24h = timestamp - 86400
        cutoff_1h = timestamp - 3600
        
        history_sent = []
        if self.use_redis and self.client:
            try:
                sent_key = self._get_sent_key(sender_id)
                self.client.zremrangebyscore(sent_key, "-inf", f"({cutoff_24h}")
                raw_sent = self.client.zrange(sent_key, 0, -1)
                for item in raw_sent:
                    try:
                        history_sent.append(json.loads(item))
                    except Exception:
                        pass
            except Exception:
                pass
        else:
            history_sent = [
                t for t in self._sent_txs[sender_id] if t["timestamp"] >= cutoff_24h
            ]

        # Filter strictly prior to current transaction
        history_prior = [t for t in history_sent if t["timestamp"] < timestamp]
        has_history = len(history_prior) > 0

        new_device = False
        geo_anomaly = False
        impossible_travel = False

        if has_history:
            history_devices = {t["device_id"] for t in history_prior if t.get("device_id")}
            if device_id and device_id not in history_devices:
                new_device = True

            history_countries = [t["country"] for t in history_prior if t.get("country")]
            history_regions = [t["region"] for t in history_prior if t.get("region")]

            if country and history_countries:
                country_mode = Counter(history_countries).most_common(1)[0][0]
                if country != country_mode:
                    geo_anomaly = True
            elif region and history_regions:
                region_mode = Counter(history_regions).most_common(1)[0][0]
                if region != region_mode:
                    geo_anomaly = True

            # Impossible travel check: transaction in last 1 hour with a different country
            recent_1h_txs = [t for t in history_prior if t["timestamp"] >= cutoff_1h]
            if country:
                for t in recent_1h_txs:
                    if t.get("country") and t["country"] != country:
                        impossible_travel = True
                        break

        return {
            "new_device": new_device,
            "geo_anomaly": geo_anomaly,
            "impossible_travel": impossible_travel,
        }



# Singleton service instance
redis_aggregate_service = RedisAggregateService()
