from datetime import datetime
from enum import StrEnum
from typing import Any

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
    currency: str = Field(..., min_length=3, max_length=3)
    timestamp: datetime
    channel: TransactionChannel
    device_id: str | None = Field(default=None, min_length=1)
    location_country: str | None = Field(default=None, min_length=2, max_length=2)
    location_region: str | None = Field(default=None, min_length=1)


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


class BatchScoreRequest(BaseModel):
    transactions: list[TransactionRequest] = Field(..., min_length=1)
    batch_id: str | None = None


class BatchPredictionError(BaseModel):
    index: int
    transaction_id: str | None = None
    code: str
    message: str


class BatchPredictionResult(BaseModel):
    index: int
    transaction_id: str | None = None
    prediction: PredictionResponse | None = None
    error: BatchPredictionError | None = None


class BatchScoreResponse(BaseModel):
    batch_id: str | None = None
    total_transactions: int
    flagged_count: int
    predictions: list[PredictionResponse] = Field(default_factory=list)
    flagged_predictions: list[PredictionResponse] = Field(default_factory=list)
    errors: list[BatchPredictionError] = Field(default_factory=list)
    results: list[BatchPredictionResult] = Field(default_factory=list)
    alert_ids: list[str] = Field(default_factory=list)


class ErrorBody(BaseModel):
    code: str
    message: str
    details: Any | None = None


class ErrorEnvelope(BaseModel):
    error: ErrorBody
