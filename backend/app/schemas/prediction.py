from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class TransactionChannel(StrEnum):
    PAYMENT = "PAYMENT"
    TRANSFER = "TRANSFER"
    CASH_OUT = "CASH_OUT"
    CASH_IN = "CASH_IN"
    DEBIT = "DEBIT"


class RiskLevel(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RuleSeverity(StrEnum):
    MINOR = "MINOR"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class TransactionRequest(BaseModel):
    transaction_id: str = Field(..., min_length=1)
    sender_id: str = Field(..., min_length=1)
    receiver_id: str = Field(..., min_length=1)
    sender_balance: float = Field(..., ge=0)
    receiver_balance: float = Field(..., ge=0)
    amount: float = Field(..., ge=0)
    currency: str = Field(default="VND", min_length=3, max_length=3)
    timestamp: datetime
    channel: TransactionChannel


class TriggeredRule(BaseModel):
    id: str
    severity: RuleSeverity
    typology: str | None = None


class TopFeature(BaseModel):
    name: str
    value: float | int | str | bool
    contribution: float | None = None


class PredictionResponse(BaseModel):
    transaction_id: str
    risk_score: float = Field(..., ge=0, le=1)
    risk_level: RiskLevel
    is_flagged: bool
    model_version: str
    triggered_rules: list[TriggeredRule] = Field(default_factory=list)
    top_features: list[TopFeature] = Field(default_factory=list)
    explanation: str | None = None
    explanation_source: str | None = None
    alert_id: str | None = None
