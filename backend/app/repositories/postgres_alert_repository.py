from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    MetaData,
    String,
    Table,
    Text,
    create_engine,
    insert,
    select,
    text,
    update,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.engine import Engine, RowMapping
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import get_settings
from app.repositories.alert_repository import AlertNotFoundError
from app.schemas.alert import Alert, AlertStatus
from app.schemas.prediction import RiskLevel, TopFeature, TriggeredRule


class PostgresRepositoryError(RuntimeError):
    """Raised when PostgreSQL persistence fails."""


metadata = MetaData()

alerts = Table(
    "alerts",
    metadata,
    Column("alert_id", String, primary_key=True),
    Column("transaction_id", String, nullable=False),
    Column("risk_score", Float, nullable=False),
    Column("risk_level", String, nullable=False),
    Column("is_flagged", Boolean, nullable=False),
    Column("triggered_rules", JSONB, nullable=False),
    Column("top_features", JSONB, nullable=False),
    Column("explanation", Text),
    Column("explanation_source", String),
    Column("status", String, nullable=False),
    Column("reviewer_id", String),
    Column("reviewed_at", DateTime(timezone=True)),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)

review_labels = Table(
    "review_labels",
    metadata,
    Column("label_id", UUID(as_uuid=True), primary_key=True),
    Column("alert_id", String, nullable=False),
    Column("transaction_id", String, nullable=False),
    Column("label", String, nullable=False),
    Column("reviewer_id", String),
    Column("created_at", DateTime(timezone=True), nullable=False),
)

prediction_logs = Table(
    "prediction_logs",
    metadata,
    Column("prediction_id", UUID(as_uuid=True), primary_key=True),
    Column("transaction_id", String, nullable=False),
    Column("risk_score", Float, nullable=False),
    Column("risk_level", String, nullable=False),
    Column("is_flagged", Boolean, nullable=False),
    Column("model_version", String, nullable=False),
    Column("triggered_rules", JSONB, nullable=False),
    Column("top_features", JSONB, nullable=False),
    Column("alert_id", String),
    Column("created_at", DateTime(timezone=True), nullable=False),
)


class PostgresAlertRepository:
    def __init__(self, database_url: str | None = None, engine: Engine | None = None) -> None:
        self.database_url = database_url or get_settings().database_url
        if not self.database_url:
            raise PostgresRepositoryError("DATABASE_URL is required for PostgreSQL persistence.")
        self.engine = engine or create_engine(
            self.database_url,
            future=True,
            pool_pre_ping=True,
        )

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
            "alert_id": f"al_{uuid4().hex[:12]}",
            "transaction_id": transaction_id,
            "risk_score": risk_score,
            "risk_level": risk_level.value,
            "is_flagged": True,
            "triggered_rules": _dump_rules(triggered_rules),
            "top_features": _dump_features(top_features),
            "explanation": explanation,
            "explanation_source": explanation_source,
            "status": AlertStatus.NEW.value,
            "reviewer_id": None,
            "reviewed_at": None,
            "created_at": now,
            "updated_at": now,
        }
        try:
            with self.engine.begin() as connection:
                inserted = connection.execute(
                    insert(alerts).values(**row).returning(alerts)
                ).mappings().one()
        except SQLAlchemyError as exc:
            raise PostgresRepositoryError(f"PostgreSQL alert create failed: {exc}") from exc
        return row_to_alert(inserted)

    def list(self, status: AlertStatus | None = None) -> list[Alert]:
        statement = select(alerts).order_by(alerts.c.created_at.desc())
        if status is not None:
            statement = statement.where(alerts.c.status == status.value)
        try:
            with self.engine.connect() as connection:
                rows = connection.execute(statement).mappings().all()
        except SQLAlchemyError as exc:
            raise PostgresRepositoryError(f"PostgreSQL alert list failed: {exc}") from exc
        return [row_to_alert(row) for row in rows]

    def get(self, alert_id: str) -> Alert:
        try:
            with self.engine.connect() as connection:
                row = connection.execute(
                    select(alerts).where(alerts.c.alert_id == alert_id).limit(1)
                ).mappings().first()
        except SQLAlchemyError as exc:
            raise PostgresRepositoryError(f"PostgreSQL alert get failed: {exc}") from exc
        if row is None:
            raise AlertNotFoundError(alert_id)
        return row_to_alert(row)

    def update_status(
        self,
        alert_id: str,
        status: AlertStatus,
        reviewer_id: str | None = None,
    ) -> Alert:
        reviewed_at = datetime.now(timezone.utc)
        try:
            with self.engine.begin() as connection:
                row = connection.execute(
                    update(alerts)
                    .where(alerts.c.alert_id == alert_id)
                    .values(
                        status=status.value,
                        reviewer_id=reviewer_id,
                        reviewed_at=reviewed_at,
                        updated_at=reviewed_at,
                    )
                    .returning(alerts)
                ).mappings().first()
                if row is None:
                    raise AlertNotFoundError(alert_id)
                if status in {AlertStatus.ESCALATED, AlertStatus.DISMISSED}:
                    connection.execute(
                        insert(review_labels).values(
                            label_id=uuid4(),
                            alert_id=alert_id,
                            transaction_id=row["transaction_id"],
                            label=status.value,
                            reviewer_id=reviewer_id,
                            created_at=reviewed_at,
                        )
                    )
        except AlertNotFoundError:
            raise
        except SQLAlchemyError as exc:
            raise PostgresRepositoryError(f"PostgreSQL alert status update failed: {exc}") from exc
        return row_to_alert(row)

    def update_explanation(
        self,
        alert_id: str,
        explanation: str,
        explanation_source: str,
    ) -> Alert:
        try:
            with self.engine.begin() as connection:
                row = connection.execute(
                    update(alerts)
                    .where(alerts.c.alert_id == alert_id)
                    .values(
                        explanation=explanation,
                        explanation_source=explanation_source,
                        updated_at=datetime.now(timezone.utc),
                    )
                    .returning(alerts)
                ).mappings().first()
        except SQLAlchemyError as exc:
            raise PostgresRepositoryError(f"PostgreSQL explanation update failed: {exc}") from exc
        if row is None:
            raise AlertNotFoundError(alert_id)
        return row_to_alert(row)

    def add_review_label(
        self,
        alert_id: str,
        status: AlertStatus,
        reviewer_id: str | None = None,
    ) -> None:
        if status not in {AlertStatus.ESCALATED, AlertStatus.DISMISSED}:
            return
        alert = self.get(alert_id)
        try:
            with self.engine.begin() as connection:
                connection.execute(
                    insert(review_labels).values(
                        label_id=uuid4(),
                        alert_id=alert_id,
                        transaction_id=alert.transaction_id,
                        label=status.value,
                        reviewer_id=reviewer_id,
                        created_at=datetime.now(timezone.utc),
                    )
                )
        except SQLAlchemyError as exc:
            raise PostgresRepositoryError(f"PostgreSQL review label insert failed: {exc}") from exc

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
        try:
            with self.engine.begin() as connection:
                connection.execute(
                    insert(prediction_logs).values(
                        prediction_id=uuid4(),
                        transaction_id=transaction_id,
                        risk_score=risk_score,
                        risk_level=risk_level.value,
                        is_flagged=is_flagged,
                        model_version=model_version,
                        triggered_rules=_dump_rules(triggered_rules),
                        top_features=_dump_features(top_features),
                        alert_id=alert_id,
                        created_at=datetime.now(timezone.utc),
                    )
                )
        except SQLAlchemyError as exc:
            raise PostgresRepositoryError(f"PostgreSQL prediction log insert failed: {exc}") from exc

    def list_prediction_logs(self) -> list[dict[str, object]]:
        try:
            with self.engine.connect() as connection:
                rows = connection.execute(
                    select(prediction_logs).order_by(prediction_logs.c.created_at.desc())
                ).mappings().all()
        except SQLAlchemyError as exc:
            raise PostgresRepositoryError(f"PostgreSQL prediction log list failed: {exc}") from exc
        return [dict(row) for row in rows]

    def ping(self) -> None:
        try:
            with self.engine.connect() as connection:
                connection.execute(text("select 1"))
        except SQLAlchemyError as exc:
            raise PostgresRepositoryError(f"PostgreSQL connectivity check failed: {exc}") from exc


def _dump_rules(rules: list[TriggeredRule]) -> list[dict[str, Any]]:
    return [rule.model_dump(mode="json") for rule in rules]


def _dump_features(features: list[TopFeature]) -> list[dict[str, Any]]:
    return [feature.model_dump(mode="json") for feature in features]


def row_to_alert(row: RowMapping | dict[str, Any]) -> Alert:
    return Alert(
        id=row["alert_id"],
        transaction_id=row["transaction_id"],
        risk_score=row["risk_score"],
        risk_level=RiskLevel(row["risk_level"]),
        status=AlertStatus(row["status"]),
        triggered_rules=[TriggeredRule(**rule) for rule in row.get("triggered_rules", [])],
        top_features=[TopFeature(**feature) for feature in row.get("top_features", [])],
        explanation=row.get("explanation"),
        explanation_source=row.get("explanation_source"),
        reviewer_id=row.get("reviewer_id"),
        reviewed_at=row.get("reviewed_at"),
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )
