from datetime import datetime, timezone
import logging

from app.llm.explainer import ExplanationResult
from app.repositories.alert_repository import alert_repository
from app.schemas.alert import Alert, AlertStatus
from app.schemas.prediction import RiskLevel, RuleSeverity, TransactionRequest, TriggeredRule
from app.services.prediction_service import PredictionService


class FakeExplainer:
    def explain(self, alert: Alert, transaction: TransactionRequest) -> ExplanationResult:
        return ExplanationResult(
            text=f"Fake explanation for {alert.id}",
            source="openai",
        )


def flagged_payload() -> TransactionRequest:
    return TransactionRequest(
        transaction_id="tx_explain_001",
        sender_id="h:sender001",
        receiver_id="h:receiver001",
        sender_balance=500_000_000,
        receiver_balance=200_000,
        amount=380_000_000,
        currency="VND",
        timestamp="2026-05-30T09:14:03+07:00",
        channel="TRANSFER",
    )


def test_prediction_service_updates_alert_explanation_with_injected_explainer() -> None:
    alert_repository.clear()
    service = PredictionService(explainer=FakeExplainer())

    prediction = service.predict(flagged_payload())
    assert prediction.alert_id is not None

    service.explain_alert(prediction.alert_id, flagged_payload())
    alert = alert_repository.get(prediction.alert_id)

    assert alert.explanation == f"Fake explanation for {prediction.alert_id}"
    assert alert.explanation_source == "openai"


def test_openai_explainer_logs_handled_failure_and_returns_template(monkeypatch, caplog) -> None:
    from app.llm import explainer

    class FakeCompletions:
        def create(self, **kwargs):
            raise TimeoutError("openai timed out")

    class FakeChat:
        completions = FakeCompletions()

    class FakeOpenAI:
        def __init__(self, api_key: str) -> None:
            self.chat = FakeChat()

    alert = Alert(
        id="alert_001",
        transaction_id="tx_explain_timeout",
        risk_score=0.91,
        risk_level=RiskLevel.HIGH,
        status=AlertStatus.OPEN,
        triggered_rules=[
            TriggeredRule(
                id="R-001",
                severity=RuleSeverity.HIGH,
                typology="velocity",
            )
        ],
        top_features=[],
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    transaction = flagged_payload()
    monkeypatch.setattr(explainer, "OpenAI", FakeOpenAI)

    with caplog.at_level(logging.ERROR):
        result = explainer.OpenAIAlertExplainer().explain(alert, transaction)

    assert result.source == "template"
    record = next(
        record for record in caplog.records if record.message == "Handled OpenAI alert explanation failure"
    )
    assert record.exc_info is not None
    assert record.transaction_id == transaction.transaction_id
    assert record.risk_level == alert.risk_level.value
    assert record.risk_score == alert.risk_score
