from app.llm.explainer import build_prompt, is_grounded, mask_value, template_explanation
from app.llm.secure_data_wrapper import secure_data_wrapper
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
            TopFeature(name="log_amount", value=19.7, contribution=0.41),
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
    assert "log_amount" in result.text


def test_mask_short_values() -> None:
    assert mask_value("short") == "***"


def test_secure_data_wrapper_masks_prompt_context() -> None:
    context = secure_data_wrapper.sanitize_transaction_context(transaction())

    assert context["sender_id"] == "h:s***001"
    assert context["receiver_id"] == "h:r***001"
    assert "sender_secret_001" not in str(context)
    assert "receiver_secret_001" not in str(context)


def test_grounding_rejects_unmasked_identifiers() -> None:
    text = "R-THRESHOLD-01 was triggered for sender h:sender_secret_001 with log_amount."

    assert is_grounded(text, alert(), transaction()) is False


def test_grounding_rejects_unsupported_rules() -> None:
    text = "R-UNKNOWN-01 was triggered with log_amount."

    assert is_grounded(text, alert(), transaction()) is False


def test_grounding_rejects_unsupported_features() -> None:
    text = "R-THRESHOLD-01 was triggered with velocity_score."

    assert is_grounded(text, alert(), transaction()) is False


def test_grounding_accepts_supported_evidence() -> None:
    text = "R-THRESHOLD-01 was triggered with log_amount."

    assert is_grounded(text, alert(), transaction()) is True
