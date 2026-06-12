from pathlib import Path

import pytest

from app.rules.engine import RuleEngine, RuleEngineError, RuleEngineManager
from app.schemas.prediction import RuleSeverity, TransactionRequest


def transaction(**overrides) -> TransactionRequest:
    payload = {
        "transaction_id": "tx_rule_001",
        "sender_id": "h:sender001",
        "receiver_id": "h:receiver001",
        "sender_balance": 10_000_000,
        "receiver_balance": 100_000,
        "amount": 8_500_000,
        "currency": "VND",
        "timestamp": "2026-05-30T09:14:03+07:00",
        "channel": "TRANSFER",
    }
    payload.update(overrides)
    return TransactionRequest(**payload)


def write_rules(tmp_path: Path, content: str) -> Path:
    path = tmp_path / "rules.yaml"
    path.write_text(content, encoding="utf-8")
    return path


def test_rule_engine_triggers_matching_rule(tmp_path: Path) -> None:
    path = write_rules(
        tmp_path,
        """
version: 1
rules:
  - id: R-BALANCE-DRAIN-01
    typology: balance_drain
    severity: MEDIUM
    enabled: true
    condition: "amount_to_sender_balance_ratio >= 0.8"
""",
    )

    engine = RuleEngine.from_file(path)
    triggered = engine.evaluate(transaction())

    assert len(triggered) == 1
    assert triggered[0].id == "R-BALANCE-DRAIN-01"
    assert triggered[0].severity == RuleSeverity.MEDIUM


def test_optional_geo_device_fields_are_backward_compatible() -> None:
    request = transaction()

    assert request.device_id is None
    assert request.location_country is None
    assert request.location_region is None


def test_optional_geo_device_rule_uses_neutral_missing_values(tmp_path: Path) -> None:
    path = write_rules(
        tmp_path,
        """
version: 1
rules:
  - id: R-GEO-01
    typology: geo_device_anomaly
    severity: MEDIUM
    enabled: true
    condition: "geo_device_evidence_available and (new_device_proxy or geo_anomaly_proxy or impossible_travel_proxy)"
""",
    )

    engine = RuleEngine.from_file(path)

    assert engine.evaluate(transaction()) == []


def test_optional_geo_device_fields_do_not_create_proxy_risk_without_history(tmp_path: Path) -> None:
    path = write_rules(
        tmp_path,
        """
version: 1
rules:
  - id: R-GEO-01
    typology: geo_device_anomaly
    severity: MEDIUM
    enabled: true
    condition: "geo_device_evidence_available and (new_device_proxy or geo_anomaly_proxy or impossible_travel_proxy)"
""",
    )

    engine = RuleEngine.from_file(path)

    assert engine.evaluate(
        transaction(
            device_id="device-demo-001",
            location_country="ZZ",
        )
    ) == []


def test_disabled_rule_does_not_trigger(tmp_path: Path) -> None:
    path = write_rules(
        tmp_path,
        """
version: 1
rules:
  - id: R-DISABLED-01
    typology: disabled
    severity: HIGH
    enabled: false
    condition: "amount >= 1"
""",
    )

    engine = RuleEngine.from_file(path)

    assert engine.evaluate(transaction()) == []


def test_duplicate_rule_ids_are_rejected(tmp_path: Path) -> None:
    path = write_rules(
        tmp_path,
        """
version: 1
rules:
  - id: R-DUP-01
    typology: one
    severity: HIGH
    condition: "amount >= 1"
  - id: R-DUP-01
    typology: two
    severity: HIGH
    condition: "amount >= 2"
""",
    )

    with pytest.raises(RuleEngineError, match="Duplicate"):
        RuleEngine.from_file(path)


def test_unknown_feature_in_condition_is_rejected(tmp_path: Path) -> None:
    path = write_rules(
        tmp_path,
        """
version: 1
rules:
  - id: R-BAD-01
    typology: bad
    severity: HIGH
    condition: "unknown_feature >= 1"
""",
    )

    with pytest.raises(RuleEngineError, match="Unknown feature"):
        RuleEngine.from_file(path)


def test_function_calls_in_condition_are_rejected(tmp_path: Path) -> None:
    path = write_rules(
        tmp_path,
        """
version: 1
rules:
  - id: R-BAD-CALL-01
    typology: bad
    severity: HIGH
    condition: "__import__('os').system('echo unsafe')"
""",
    )

    with pytest.raises(RuleEngineError, match="Unsupported expression node"):
        RuleEngine.from_file(path)


def test_reload_rejects_invalid_rules_and_keeps_previous_engine(tmp_path: Path) -> None:
    path = write_rules(
        tmp_path,
        """
version: 1
rules:
  - id: R-OK-01
    typology: ok
    severity: HIGH
    condition: "amount >= 1"
""",
    )
    manager = RuleEngineManager(path)
    previous_engine = manager.engine

    path.write_text(
        """
version: 2
rules:
  - id: R-BAD-01
    typology: bad
    severity: HIGH
    condition: "unknown_feature >= 1"
""",
        encoding="utf-8",
    )

    with pytest.raises(RuleEngineError, match="Unknown feature"):
        manager.reload()

    assert manager.engine is previous_engine
    assert manager.engine.version == 1
