from __future__ import annotations

from app.repositories.alert_repository import AlertRepository
from app.repositories.factory import get_alert_repository
from app.schemas.alert import Alert, AlertStatus
from app.schemas.prediction import PredictionResponse, RiskLevel, TopFeature, TriggeredRule


class AlertService:
    def __init__(self, repository: AlertRepository | None = None) -> None:
        self.repository = repository or get_alert_repository()

    def create_alert(
        self,
        transaction_id: str,
        risk_score: float,
        risk_level: RiskLevel,
        triggered_rules: list[TriggeredRule],
        top_features: list[TopFeature],
    ) -> Alert:
        return self.repository.create(
            transaction_id=transaction_id,
            risk_score=risk_score,
            risk_level=risk_level,
            triggered_rules=triggered_rules,
            top_features=top_features,
        )

    def list_alerts(self, status: AlertStatus | None = None) -> list[Alert]:
        return self.repository.list(status=status)

    def get_alert(self, alert_id: str) -> Alert:
        return self.repository.get(alert_id)

    def update_status(
        self,
        alert_id: str,
        status: AlertStatus,
        reviewer_id: str | None = None,
    ) -> Alert:
        alert = self.repository.update_status(alert_id, status, reviewer_id)
        if status in {AlertStatus.ESCALATED, AlertStatus.DISMISSED}:
            self.repository.add_review_label(alert_id, status, reviewer_id)
        return alert

    def update_explanation(
        self,
        alert_id: str,
        explanation: str,
        explanation_source: str,
    ) -> Alert:
        return self.repository.update_explanation(
            alert_id=alert_id,
            explanation=explanation,
            explanation_source=explanation_source,
        )

    def create_prediction_log(self, response: PredictionResponse) -> None:
        create_prediction_log = getattr(self.repository, "create_prediction_log", None)
        if create_prediction_log is None:
            return

        create_prediction_log(
            transaction_id=response.transaction_id,
            risk_score=response.risk_score,
            risk_level=response.risk_level,
            is_flagged=response.is_flagged,
            model_version=response.model_version,
            triggered_rules=response.triggered_rules,
            top_features=response.top_features,
            alert_id=response.alert_id,
        )

    def list_prediction_logs(self) -> list[dict[str, object]]:
        list_prediction_logs = getattr(self.repository, "list_prediction_logs", None)
        if list_prediction_logs is None:
            return []
        return list_prediction_logs()
