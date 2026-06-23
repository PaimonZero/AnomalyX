from __future__ import annotations

from datetime import datetime, timezone
import pytest

from app.features.redis_aggregates import redis_aggregate_service
from app.features.service import feature_service
from app.schemas.prediction import TransactionChannel, TransactionRequest


@pytest.fixture(autouse=True)
def clean_redis_aggregates():
    redis_aggregate_service.clear()
    yield
    redis_aggregate_service.clear()


def make_tx_request(
    amount: float,
    sender_id: str = "sender_123",
    receiver_id: str = "receiver_abc",
    timestamp: datetime = None,
    channel: TransactionChannel = TransactionChannel.TRANSFER,
    device_id: str | None = "device_x",
    country: str | None = "VN",
    region: str | None = "HN",
) -> TransactionRequest:
    if timestamp is None:
        timestamp = datetime(2026, 6, 22, 12, 0, 0, tzinfo=timezone.utc)
    return TransactionRequest(
        transaction_id=f"tx_{int(timestamp.timestamp())}_{amount}",
        sender_id=sender_id,
        receiver_id=receiver_id,
        amount=amount,
        currency="VND",
        sender_balance=1_000_000_000.0,
        receiver_balance=50_000_000.0,
        channel=channel,
        timestamp=timestamp,
        device_id=device_id,
        location_country=country,
        location_region=region,
    )


def test_cold_start_returns_defaults():
    # When a new transaction is processed and the sender has no history
    tx = make_tx_request(amount=100_000.0, sender_id="new_sender")
    
    # Compute features before recording the transaction
    features = feature_service.compute(tx).values
    
    assert features["has_history"] is False
    assert features["tx_count_1h"] == 1
    assert features["tx_count_24h"] == 1
    assert features["sum_amount_1h"] == 100_000.0
    assert features["sum_amount_24h"] == 100_000.0
    assert features["distinct_receivers_1h"] == 1
    assert features["distinct_receivers_24h"] == 1
    assert features["count_just_below_threshold_24h"] == 0
    assert features["new_device_proxy"] is False
    assert features["geo_anomaly_proxy"] is False
    assert features["impossible_travel_proxy"] is False
    assert features["velocity_vs_baseline_ratio_proxy"] == 1.0


def test_record_and_get_tx_count():
    sender = "sender_1"
    base_time = datetime(2026, 6, 22, 12, 0, 0, tzinfo=timezone.utc)
    
    # Record 4 prior transactions (e.g. every 10 minutes)
    for i in range(4):
        tx_time = base_time.replace(minute=i * 10)
        redis_aggregate_service.record_transaction(
            tx_id=f"prior_{i}",
            sender_id=sender,
            receiver_id=f"receiver_{i}",
            amount=50_000.0,
            timestamp=tx_time.timestamp(),
            channel="TRANSFER",
            device_id="device_1",
            country="VN",
            region="HN",
        )
        
    # Fifth transaction at 12:45
    current_tx = make_tx_request(
        amount=100_000.0,
        sender_id=sender,
        timestamp=base_time.replace(minute=45),
        device_id="device_1",
    )
    
    features = feature_service.compute(current_tx).values
    assert features["has_history"] is True
    # 4 prior + 1 current = 5
    assert features["tx_count_1h"] == 5
    assert features["tx_count_24h"] == 5
    assert features["sum_amount_1h"] == 4 * 50_000.0 + 100_000.0


def test_sum_amount_window():
    sender = "sender_2"
    base_time = datetime(2026, 6, 22, 12, 0, 0, tzinfo=timezone.utc)
    
    # Record 1 txn 2 hours ago
    redis_aggregate_service.record_transaction(
        tx_id="tx_old",
        sender_id=sender,
        receiver_id="receiver_1",
        amount=500_000.0,
        timestamp=(base_time.timestamp() - 7200),
        channel="TRANSFER",
    )
    
    # Record 1 txn 30 mins ago
    redis_aggregate_service.record_transaction(
        tx_id="tx_recent",
        sender_id=sender,
        receiver_id="receiver_1",
        amount=300_000.0,
        timestamp=(base_time.timestamp() - 1800),
        channel="TRANSFER",
    )
    
    # Current txn
    current_tx = make_tx_request(
        amount=200_000.0,
        sender_id=sender,
        timestamp=base_time,
    )
    
    features = feature_service.compute(current_tx).values
    # tx_count_1h should be 2 (tx_recent + current_tx)
    assert features["tx_count_1h"] == 2
    # tx_count_24h should be 3 (tx_old + tx_recent + current_tx)
    assert features["tx_count_24h"] == 3
    
    assert features["sum_amount_1h"] == 300_000.0 + 200_000.0
    assert features["sum_amount_24h"] == 500_000.0 + 300_000.0 + 200_000.0


def test_distinct_receivers():
    sender = "sender_3"
    base_time = datetime(2026, 6, 22, 12, 0, 0, tzinfo=timezone.utc)
    
    # Record txns to 2 unique receivers
    redis_aggregate_service.record_transaction(
        tx_id="tx1",
        sender_id=sender,
        receiver_id="rec_A",
        amount=10_000.0,
        timestamp=base_time.timestamp() - 600,
        channel="TRANSFER",
    )
    redis_aggregate_service.record_transaction(
        tx_id="tx2",
        sender_id=sender,
        receiver_id="rec_B",
        amount=10_000.0,
        timestamp=base_time.timestamp() - 300,
        channel="TRANSFER",
    )
    
    # Current transaction to rec_C
    current_tx = make_tx_request(
        amount=10_000.0,
        sender_id=sender,
        receiver_id="rec_C",
        timestamp=base_time,
    )
    
    features = feature_service.compute(current_tx).values
    assert features["distinct_receivers_1h"] == 3
    assert features["distinct_receivers_24h"] == 3


def test_count_just_below_threshold():
    sender = "sender_4"
    base_time = datetime(2026, 6, 22, 12, 0, 0, tzinfo=timezone.utc)
    
    # Threshold is 400M. "Just below" is [360M, 400M)
    # Record 2 txns in the window that are just below threshold
    redis_aggregate_service.record_transaction(
        tx_id="tx_below1",
        sender_id=sender,
        receiver_id="rec_1",
        amount=380_000_000.0,
        timestamp=base_time.timestamp() - 3600,
        channel="TRANSFER",
    )
    # 1 txn that is NOT just below (too small)
    redis_aggregate_service.record_transaction(
        tx_id="tx_small",
        sender_id=sender,
        receiver_id="rec_1",
        amount=100_000_000.0,
        timestamp=base_time.timestamp() - 1800,
        channel="TRANSFER",
    )
    # 1 txn that is exactly at threshold
    redis_aggregate_service.record_transaction(
        tx_id="tx_exact",
        sender_id=sender,
        receiver_id="rec_1",
        amount=400_000_000.0,
        timestamp=base_time.timestamp() - 900,
        channel="TRANSFER",
    )
    
    # Current transaction is just below threshold
    current_tx = make_tx_request(
        amount=390_000_000.0,
        sender_id=sender,
        timestamp=base_time,
    )
    
    features = feature_service.compute(current_tx).values
    # Should count: tx_below1 + current_tx = 2
    assert features["count_just_below_threshold_24h"] == 2
    assert features["sum_just_below_threshold_24h"] == 380_000_000.0 + 390_000_000.0


def test_window_expiry():
    sender = "sender_5"
    base_time = datetime(2026, 6, 22, 12, 0, 0, tzinfo=timezone.utc)
    
    # Transaction 25 hours ago
    redis_aggregate_service.record_transaction(
        tx_id="tx_old",
        sender_id=sender,
        receiver_id="rec_1",
        amount=10_000.0,
        timestamp=base_time.timestamp() - (25 * 3600),
        channel="TRANSFER",
    )
    
    # Current txn
    current_tx = make_tx_request(
        amount=20_000.0,
        sender_id=sender,
        timestamp=base_time,
    )
    
    features = feature_service.compute(current_tx).values
    assert features["tx_count_24h"] == 1  # Only current txn remains
    assert features["sum_amount_24h"] == 20_000.0
