from __future__ import annotations

from app.repositories.alert_repository import AlertRepository
from app.repositories.factory import get_alert_repository
from app.schemas.alert import Alert, AlertStatus
from app.schemas.prediction import RiskLevel, TopFeature, TriggeredRule


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

    def update_status(self, alert_id: str, status: AlertStatus) -> Alert:
        return self.repository.update_status(alert_id, status)

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
