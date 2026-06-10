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

    def update_status(
        self,
        alert_id: str,
        status: AlertStatus,
        reviewer_id: str | None = None,
    ) -> Alert:
        """Update alert review status."""

    def update_explanation(
        self,
        alert_id: str,
        explanation: str,
        explanation_source: str,
    ) -> Alert:
        """Persist an alert explanation."""

    def add_review_label(
        self,
        alert_id: str,
        status: AlertStatus,
        reviewer_id: str | None = None,
    ) -> None:
        """Record a ground-truth review label for retraining."""

    def create_prediction_log(
        self,
        transaction_id: str,
        risk_score: float,
        risk_level: RiskLevel,
        is_flagged: bool,
        model_version: str,
        triggered_rules: list[TriggeredRule],
        top_features: list[TopFeature],
        alert_id: str | None = None,
    ) -> None:
        """Persist a prediction audit record."""

    def list_prediction_logs(self) -> list[dict[str, object]]:
        """Return prediction audit records when supported."""


class InMemoryAlertRepository:
    def __init__(self) -> None:
        self._alerts: dict[str, Alert] = {}
        self._review_labels: list[dict[str, object]] = []
        self._prediction_logs: list[dict[str, object]] = []
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
            status=AlertStatus.NEW,
            triggered_rules=triggered_rules,
            top_features=top_features,
            explanation=explanation,
            explanation_source=explanation_source,
            reviewer_id=None,
            reviewed_at=None,
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

    def update_status(
        self,
        alert_id: str,
        status: AlertStatus,
        reviewer_id: str | None = None,
    ) -> Alert:
        reviewed_at = datetime.now(timezone.utc)
        with self._lock:
            alert = self._alerts.get(alert_id)
            if alert is None:
                raise AlertNotFoundError(alert_id)

            updated_alert = alert.model_copy(
                update={
                    "status": status,
                    "reviewer_id": reviewer_id,
                    "reviewed_at": reviewed_at,
                    "updated_at": reviewed_at,
                }
            )
            self._alerts[alert_id] = updated_alert
            if status in {AlertStatus.ESCALATED, AlertStatus.DISMISSED}:
                self._review_labels.append(
                    {
                        "alert_id": alert_id,
                        "status": status.value,
                        "reviewer_id": reviewer_id,
                        "created_at": reviewed_at,
                    }
                )

        return updated_alert

    def add_review_label(
        self,
        alert_id: str,
        status: AlertStatus,
        reviewer_id: str | None = None,
    ) -> None:
        with self._lock:
            self._review_labels.append(
                {
                    "alert_id": alert_id,
                    "status": status.value,
                    "reviewer_id": reviewer_id,
                    "created_at": datetime.now(timezone.utc),
                }
            )

    def list_review_labels(self) -> list[dict[str, object]]:
        with self._lock:
            return list(self._review_labels)

    def clear_review_labels(self) -> None:
        with self._lock:
            self._review_labels.clear()

    def create_prediction_log(
        self,
        transaction_id: str,
        risk_score: float,
        risk_level: RiskLevel,
        is_flagged: bool,
        model_version: str,
        triggered_rules: list[TriggeredRule],
        top_features: list[TopFeature],
        alert_id: str | None = None,
    ) -> None:
        with self._lock:
            self._prediction_logs.append(
                {
                    "transaction_id": transaction_id,
                    "risk_score": risk_score,
                    "risk_level": risk_level.value,
                    "is_flagged": is_flagged,
                    "model_version": model_version,
                    "triggered_rules": [rule.model_dump(mode="json") for rule in triggered_rules],
                    "top_features": [feature.model_dump(mode="json") for feature in top_features],
                    "alert_id": alert_id,
                    "created_at": datetime.now(timezone.utc),
                }
            )

    def list_prediction_logs(self) -> list[dict[str, object]]:
        with self._lock:
            return list(self._prediction_logs)

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
            self._review_labels.clear()
            self._prediction_logs.clear()


alert_repository = InMemoryAlertRepository()
