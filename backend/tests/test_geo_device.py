from __future__ import annotations

from datetime import datetime, timezone
import pytest

from app.features.redis_aggregates import redis_aggregate_service
from app.features.service import feature_service
from app.rules.engine import rule_engine_manager
from app.schemas.prediction import TransactionChannel, TransactionRequest


@pytest.fixture(autouse=True)
def clean_redis_aggregates():
    redis_aggregate_service.clear()
    yield
    redis_aggregate_service.clear()


def make_tx_request(
    amount: float = 100_000.0,
    sender_id: str = "sender_geo",
    receiver_id: str = "rec_geo",
    timestamp: datetime = None,
    channel: TransactionChannel = TransactionChannel.TRANSFER,
    device_id: str | None = "device_1",
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


def test_cold_start_no_anomaly():
    # If there is no history, everything is False (no baseline)
    tx = make_tx_request(sender_id="cold_sender", device_id="device_new", country="US")
    features = feature_service.compute(tx).values
    
    assert features["new_device"] is False
    assert features["geo_anomaly"] is False
    assert features["impossible_travel"] is False


def test_new_device_detected():
    sender = "sender_dev_test"
    base_time = datetime(2026, 6, 22, 12, 0, 0, tzinfo=timezone.utc)
    
    # 1. Record a txn with device_1
    redis_aggregate_service.record_transaction(
        tx_id="tx_dev1",
        sender_id=sender,
        receiver_id="rec_1",
        amount=50_000.0,
        timestamp=base_time.timestamp() - 3600,
        channel="TRANSFER",
        device_id="device_1",
        country="VN",
    )
    
    # 2. Current txn is from device_2
    tx = make_tx_request(sender_id=sender, timestamp=base_time, device_id="device_2", country="VN")
    features = feature_service.compute(tx).values
    
    assert features["new_device"] is True
    assert features["geo_anomaly"] is False


def test_known_device_no_flag():
    sender = "sender_dev_known"
    base_time = datetime(2026, 6, 22, 12, 0, 0, tzinfo=timezone.utc)
    
    # 1. Record txn from device_1
    redis_aggregate_service.record_transaction(
        tx_id="tx_dev1",
        sender_id=sender,
        receiver_id="rec_1",
        amount=50_000.0,
        timestamp=base_time.timestamp() - 3600,
        channel="TRANSFER",
        device_id="device_1",
        country="VN",
    )
    
    # 2. Current txn is also from device_1
    tx = make_tx_request(sender_id=sender, timestamp=base_time, device_id="device_1", country="VN")
    features = feature_service.compute(tx).values
    
    assert features["new_device"] is False


def test_geo_anomaly_different_country():
    sender = "sender_geo_anom"
    base_time = datetime(2026, 6, 22, 12, 0, 0, tzinfo=timezone.utc)
    
    # 1. Record 3 transactions from VN
    for i in range(3):
        redis_aggregate_service.record_transaction(
            tx_id=f"tx_vn_{i}",
            sender_id=sender,
            receiver_id="rec_1",
            amount=50_000.0,
            timestamp=base_time.timestamp() - 7200 - i * 100,
            channel="TRANSFER",
            device_id="device_1",
            country="VN",
        )
        
    # 2. Current transaction is from US (which is not mode)
    tx = make_tx_request(sender_id=sender, timestamp=base_time, device_id="device_1", country="US")
    features = feature_service.compute(tx).values
    
    assert features["geo_anomaly"] is True
    # impossible_travel should also be True because country changed within 2h (cutoff is 1h, wait, 7200s is 2h, so VN txn is outside 1h window)
    # Let's verify: cutoff_1h = base_time - 3600. The VN txns are -7200, so impossible_travel should be False.
    assert features["impossible_travel"] is False


def test_impossible_travel_detected():
    sender = "sender_travel"
    base_time = datetime(2026, 6, 22, 12, 0, 0, tzinfo=timezone.utc)
    
    # 1. Transaction in VN 30 minutes ago
    redis_aggregate_service.record_transaction(
        tx_id="tx_vn",
        sender_id=sender,
        receiver_id="rec_1",
        amount=50_000.0,
        timestamp=base_time.timestamp() - 1800,
        channel="TRANSFER",
        device_id="device_1",
        country="VN",
    )
    
    # 2. Current transaction from SG (Singapore)
    tx = make_tx_request(sender_id=sender, timestamp=base_time, device_id="device_1", country="SG")
    features = feature_service.compute(tx).values
    
    assert features["impossible_travel"] is True


def test_rule_geo_01_fires():
    sender = "sender_rule_geo"
    base_time = datetime(2026, 6, 22, 12, 0, 0, tzinfo=timezone.utc)
    
    # 1. Record prior VN transaction
    redis_aggregate_service.record_transaction(
        tx_id="tx_vn",
        sender_id=sender,
        receiver_id="rec_1",
        amount=50_000.0,
        timestamp=base_time.timestamp() - 1800,
        channel="TRANSFER",
        device_id="device_1",
        country="VN",
    )
    
    # 2. Current transaction is SG (triggers impossible travel & new device & geo anomaly)
    tx = make_tx_request(sender_id=sender, timestamp=base_time, device_id="device_2", country="SG")
    
    # Evaluate rules
    triggered = rule_engine_manager.engine.evaluate(tx)
    triggered_ids = {r.id for r in triggered}
    
    # R-GEO-01 should trigger because geo_device_evidence_available is True and impossible_travel/new_device/geo_anomaly are True
    assert "R-GEO-01" in triggered_ids
