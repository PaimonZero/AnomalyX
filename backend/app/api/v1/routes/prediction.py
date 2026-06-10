from fastapi import APIRouter, BackgroundTasks, Header

from app.schemas.prediction import (
    BatchScoreRequest,
    BatchScoreResponse,
    PredictionResponse,
    TransactionRequest,
)
from app.services.prediction_service import PredictionService


router = APIRouter()


@router.post("/predict", response_model=PredictionResponse)
def predict_transaction(
    transaction: TransactionRequest,
    background_tasks: BackgroundTasks,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> PredictionResponse:
    return PredictionService().predict(
        transaction,
        background_tasks=background_tasks,
        idempotency_key=idempotency_key,
    )


@router.post("/batch-score", response_model=BatchScoreResponse)
def batch_score_transactions(
    payload: BatchScoreRequest,
    background_tasks: BackgroundTasks,
) -> BatchScoreResponse:
    predictions = PredictionService().batch_predict(
        payload.transactions,
        background_tasks=background_tasks,
    )
    flagged_predictions = [prediction for prediction in predictions if prediction.is_flagged]
    alert_ids = [
        prediction.alert_id
        for prediction in flagged_predictions
        if prediction.alert_id is not None
    ]
    return BatchScoreResponse(
        batch_id=payload.batch_id,
        total_transactions=len(predictions),
        flagged_count=len(flagged_predictions),
        predictions=predictions,
        flagged_predictions=flagged_predictions,
        alert_ids=alert_ids,
    )
