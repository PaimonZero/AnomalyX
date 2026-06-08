from fastapi import APIRouter, BackgroundTasks, Header

from app.schemas.prediction import PredictionResponse, TransactionRequest
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
