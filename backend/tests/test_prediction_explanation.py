from app.llm.explainer import ExplanationResult
from app.repositories.alert_repository import alert_repository
from app.schemas.alert import Alert
from app.schemas.prediction import TransactionRequest
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
