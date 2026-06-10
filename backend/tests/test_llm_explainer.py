from app.llm.explainer import build_prompt, mask_value, template_explanation
from app.schemas.alert import AlertStatus
from app.schemas.prediction import RiskLevel, RuleSeverity, TopFeature, TransactionRequest, TriggeredRule
from app.repositories.alert_repository import InMemoryAlertRepository


def transaction() -> TransactionRequest:
    return TransactionRequest(
        transaction_id="tx_sensitive_123456",
        sender_id="h:sender_secret_001",
        receiver_id="h:receiver_secret_001",
        sender_balance=500_000_000,
        receiver_balance=200_000,
        amount=380_000_000,
        currency="VND",
        timestamp="2026-05-30T09:14:03+07:00",
        channel="TRANSFER",
    )


def alert():
    repo = InMemoryAlertRepository()
    return repo.create(
        transaction_id="tx_sensitive_123456",
        risk_score=0.82,
        risk_level=RiskLevel.HIGH,
        triggered_rules=[
            TriggeredRule(
                id="R-THRESHOLD-01",
                severity=RuleSeverity.HIGH,
                typology="threshold_avoidance",
            )
        ],
        top_features=[
            TopFeature(name="mock_log_amount", value=19.7, contribution=0.41),
        ],
    )


def test_prompt_masks_identifiers() -> None:
    prompt = build_prompt(alert(), transaction(), language="vi,en")

    assert "sender_secret_001" not in prompt
    assert "receiver_secret_001" not in prompt
    assert "h:s***001" in prompt
    assert "h:r***001" in prompt


def test_template_explanation_uses_supplied_evidence() -> None:
    result = template_explanation(alert())

    assert result.source == "template"
    assert "R-THRESHOLD-01" in result.text
    assert "mock_log_amount" in result.text


def test_mask_short_values() -> None:
    assert mask_value("short") == "***"
