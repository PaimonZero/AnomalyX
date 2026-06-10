from __future__ import annotations

from datetime import datetime, timezone
from threading import Lock
from typing import Protocol
from uuid import uuid4

from app.schemas.alert import Alert, AlertStatus
from app.schemas.prediction import RiskLevel, TopFeature, TriggeredRule


class AlertNotFoundError(KeyError):
    """Raised when an alert id does not exist."""


class AlertRepository(Protocol):
    def create(
        self,
        transaction_id: str,
        risk_score: float,
        risk_level: RiskLevel,
        triggered_rules: list[TriggeredRule],
        top_features: list[TopFeature],
        explanation: str | None = None,
        explanation_source: str | None = None,
    ) -> Alert:
        """Create an alert."""

    def list(self, status: AlertStatus | None = None) -> list[Alert]:
        """List alerts."""

    def get(self, alert_id: str) -> Alert:
        """Get one alert by id."""

    def update_status(self, alert_id: str, status: AlertStatus) -> Alert:
        """Update alert review status."""

    def update_explanation(
        self,
        alert_id: str,
        explanation: str,
        explanation_source: str,
    ) -> Alert:
        """Persist an alert explanation."""


class InMemoryAlertRepository:
    def __init__(self) -> None:
        self._alerts: dict[str, Alert] = {}
        self._lock = Lock()

    def create(
        self,
        transaction_id: str,
        risk_score: float,
        risk_level: RiskLevel,
        triggered_rules: list[TriggeredRule],
        top_features: list[TopFeature],
        explanation: str | None = None,
        explanation_source: str | None = None,
    ) -> Alert:
        now = datetime.now(timezone.utc)
        alert = Alert(
            id=f"al_{uuid4().hex[:12]}",
            transaction_id=transaction_id,
            risk_score=risk_score,
            risk_level=risk_level,
            status=AlertStatus.OPEN,
            triggered_rules=triggered_rules,
            top_features=top_features,
            explanation=explanation,
            explanation_source=explanation_source,
            created_at=now,
            updated_at=now,
        )

        with self._lock:
            self._alerts[alert.id] = alert

        return alert

    def list(self, status: AlertStatus | None = None) -> list[Alert]:
        with self._lock:
            alerts = list(self._alerts.values())

        if status is not None:
            alerts = [alert for alert in alerts if alert.status == status]

        return sorted(alerts, key=lambda alert: alert.created_at, reverse=True)

    def get(self, alert_id: str) -> Alert:
        with self._lock:
            alert = self._alerts.get(alert_id)

        if alert is None:
            raise AlertNotFoundError(alert_id)

        return alert

    def update_status(self, alert_id: str, status: AlertStatus) -> Alert:
        with self._lock:
            alert = self._alerts.get(alert_id)
            if alert is None:
                raise AlertNotFoundError(alert_id)

            updated_alert = alert.model_copy(
                update={
                    "status": status,
                    "updated_at": datetime.now(timezone.utc),
                }
            )
            self._alerts[alert_id] = updated_alert

        return updated_alert

    def update_explanation(
        self,
        alert_id: str,
        explanation: str,
        explanation_source: str,
    ) -> Alert:
        with self._lock:
            alert = self._alerts.get(alert_id)
            if alert is None:
                raise AlertNotFoundError(alert_id)

            updated_alert = alert.model_copy(
                update={
                    "explanation": explanation,
                    "explanation_source": explanation_source,
                    "updated_at": datetime.now(timezone.utc),
                }
            )
            self._alerts[alert_id] = updated_alert

        return updated_alert

    def clear(self) -> None:
        with self._lock:
            self._alerts.clear()


alert_repository = InMemoryAlertRepository()
