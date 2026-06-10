import pytest

from app.core.decision import DecisionEngine
from app.schemas.prediction import RiskLevel, RuleSeverity, TriggeredRule


def make_engine() -> DecisionEngine:
    return DecisionEngine(medium_threshold=0.40, flag_threshold=0.70)


def test_critical_rule_overrides_any_ml_score() -> None:
    result = make_engine().decide(
        risk_score=0.01,
        triggered_rules=[
            TriggeredRule(id="R-CRIT-01", severity=RuleSeverity.CRITICAL),
        ],
    )

    assert result.risk_level == RiskLevel.CRITICAL
    assert result.is_flagged is True
    assert result.reason == "critical_rule_override"


def test_high_rule_overrides_low_ml_score() -> None:
    result = make_engine().decide(
        risk_score=0.10,
        triggered_rules=[
            TriggeredRule(id="R-STRUCT-01", severity=RuleSeverity.HIGH),
        ],
    )

    assert result.risk_level == RiskLevel.HIGH
    assert result.is_flagged is True
    assert result.reason == "high_rule_override"


def test_high_ml_score_flags_without_rules() -> None:
    result = make_engine().decide(risk_score=0.70, triggered_rules=[])

    assert result.risk_level == RiskLevel.HIGH
    assert result.is_flagged is True
    assert result.reason == "ml_score_flag_threshold"


def test_medium_ml_score_is_log_only() -> None:
    result = make_engine().decide(
        risk_score=0.40,
        triggered_rules=[
            TriggeredRule(id="R-VELO-01", severity=RuleSeverity.MINOR),
        ],
    )

    assert result.risk_level == RiskLevel.MEDIUM
    assert result.is_flagged is False
    assert result.reason == "ml_score_medium_threshold"


def test_low_ml_score_without_strong_rules_is_low() -> None:
    result = make_engine().decide(
        risk_score=0.39,
        triggered_rules=[
            TriggeredRule(id="R-GEO-01", severity=RuleSeverity.MEDIUM),
        ],
    )

    assert result.risk_level == RiskLevel.LOW
    assert result.is_flagged is False
    assert result.reason == "low_risk"


def test_invalid_score_is_rejected() -> None:
    with pytest.raises(ValueError, match="risk_score"):
        make_engine().decide(risk_score=1.2, triggered_rules=[])


def test_invalid_threshold_order_is_rejected() -> None:
    with pytest.raises(ValueError, match="Risk thresholds"):
        DecisionEngine(medium_threshold=0.70, flag_threshold=0.40)
