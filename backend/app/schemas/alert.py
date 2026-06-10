from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from app.schemas.prediction import RiskLevel, TopFeature, TriggeredRule


class AlertStatus(StrEnum):
    NEW = "NEW"
    ESCALATED = "ESCALATED"
    DISMISSED = "DISMISSED"


class Alert(BaseModel):
    id: str
    transaction_id: str
    risk_score: float = Field(..., ge=0, le=1)
    risk_level: RiskLevel
    status: AlertStatus
    triggered_rules: list[TriggeredRule] = Field(default_factory=list)
    top_features: list[TopFeature] = Field(default_factory=list)
    explanation: str | None = None
    explanation_source: str | None = None
    reviewer_id: str | None = Field(default=None, max_length=128)
    reviewed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class AlertStatusUpdate(BaseModel):
    status: AlertStatus
    reviewer_id: str | None = Field(default=None, max_length=128)
