from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any
from urllib import error, parse, request
from uuid import uuid4

from app.core.config import get_settings
from app.repositories.alert_repository import AlertNotFoundError
from app.schemas.alert import Alert, AlertStatus
from app.schemas.prediction import RiskLevel, TopFeature, TriggeredRule


class SupabaseError(RuntimeError):
    """Raised when Supabase returns an unexpected response."""


class SupabaseAlertRepository:
    def __init__(
        self,
        supabase_url: str | None = None,
        service_role_key: str | None = None,
        schema: str | None = None,
    ) -> None:
        settings = get_settings()
        self.supabase_url = (supabase_url or settings.supabase_url).rstrip("/")
        self.service_role_key = service_role_key or settings.supabase_service_role_key
        self.schema = schema or settings.supabase_schema
        if not self.supabase_url or not self.service_role_key:
            raise SupabaseError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are required.")

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
        row = {
            "id": f"al_{uuid4().hex[:12]}",
            "transaction_id": transaction_id,
            "risk_score": risk_score,
            "risk_level": risk_level.value,
            "status": AlertStatus.OPEN.value,
            "triggered_rules": [rule.model_dump(mode="json") for rule in triggered_rules],
            "top_features": [feature.model_dump(mode="json") for feature in top_features],
            "explanation": explanation,
            "explanation_source": explanation_source,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
        }
        rows = self._request(
            method="POST",
            table="alerts",
            body=row,
            extra_headers={"Prefer": "return=representation"},
        )
        return row_to_alert(rows[0])

    def list(self, status: AlertStatus | None = None) -> list[Alert]:
        query = {
            "select": "*",
            "order": "created_at.desc",
        }
        if status is not None:
            query["status"] = f"eq.{status.value}"

        rows = self._request(method="GET", table="alerts", query=query)
        return [row_to_alert(row) for row in rows]

    def get(self, alert_id: str) -> Alert:
        rows = self._request(
            method="GET",
            table="alerts",
            query={
                "select": "*",
                "id": f"eq.{alert_id}",
                "limit": "1",
            },
        )
        if not rows:
            raise AlertNotFoundError(alert_id)
        return row_to_alert(rows[0])

    def update_status(self, alert_id: str, status: AlertStatus) -> Alert:
        return self._patch_alert(
            alert_id=alert_id,
            values={
                "status": status.value,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
        )

    def update_explanation(
        self,
        alert_id: str,
        explanation: str,
        explanation_source: str,
    ) -> Alert:
        return self._patch_alert(
            alert_id=alert_id,
            values={
                "explanation": explanation,
                "explanation_source": explanation_source,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
        )

    def clear(self) -> None:
        raise SupabaseError("clear() is disabled for Supabase persistence.")

    def _patch_alert(self, alert_id: str, values: dict[str, Any]) -> Alert:
        rows = self._request(
            method="PATCH",
            table="alerts",
            query={"id": f"eq.{alert_id}"},
            body=values,
            extra_headers={"Prefer": "return=representation"},
        )
        if not rows:
            raise AlertNotFoundError(alert_id)
        return row_to_alert(rows[0])

    def _request(
        self,
        method: str,
        table: str,
        query: dict[str, str] | None = None,
        body: dict[str, Any] | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> list[dict[str, Any]]:
        url = f"{self.supabase_url}/rest/v1/{table}"
        if query:
            url = f"{url}?{parse.urlencode(query)}"

        data = None
        if body is not None:
            data = json.dumps(body).encode("utf-8")

        headers = {
            "apikey": self.service_role_key,
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Accept-Profile": self.schema,
            "Content-Profile": self.schema,
        }
        if extra_headers:
            headers.update(extra_headers)

        req = request.Request(url, data=data, headers=headers, method=method)
        try:
            with request.urlopen(req, timeout=20) as response:
                payload = response.read().decode("utf-8")
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise SupabaseError(f"Supabase {method} {table} failed: HTTP {exc.code} {detail}") from exc

        if not payload:
            return []
        decoded = json.loads(payload)
        if isinstance(decoded, list):
            return decoded
        if isinstance(decoded, dict):
            return [decoded]
        raise SupabaseError(f"Unexpected Supabase response shape: {type(decoded).__name__}")


def row_to_alert(row: dict[str, Any]) -> Alert:
    return Alert(
        id=row["id"],
        transaction_id=row["transaction_id"],
        risk_score=row["risk_score"],
        risk_level=RiskLevel(row["risk_level"]),
        status=AlertStatus(row["status"]),
        triggered_rules=[TriggeredRule(**rule) for rule in row.get("triggered_rules", [])],
        top_features=[TopFeature(**feature) for feature in row.get("top_features", [])],
        explanation=row.get("explanation"),
        explanation_source=row.get("explanation_source"),
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )
