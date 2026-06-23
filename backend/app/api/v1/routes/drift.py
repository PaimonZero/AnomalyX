from __future__ import annotations

from typing import Any
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.core.drift import score_drift_detector
from app.core.metrics import set_model_drift_psi

router = APIRouter(prefix="/drift")


class BaselineRequest(BaseModel):
    scores: list[float] = Field(..., description="List of prediction scores to set as the baseline.")


class DriftStatusResponse(BaseModel):
    psi: float = Field(..., description="Current Population Stability Index (PSI).")
    recent_scores_count: int = Field(..., description="Number of scores currently in rolling window.")
    baseline_scores_count: int = Field(..., description="Number of scores in baseline.")
    drift_status: str = Field(..., description="Drift classification: NO_DRIFT, WARNING, or DRIFT.")


@router.post(
    "/baseline",
    status_code=status.HTTP_200_OK,
    summary="Set baseline score distribution",
)
def set_baseline(payload: BaselineRequest) -> dict[str, Any]:
    if not payload.scores:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Scores list cannot be empty.",
        )
    try:
        score_drift_detector.set_baseline(payload.scores)
        # Recalculate PSI with new baseline
        psi = score_drift_detector.compute_psi()
        set_model_drift_psi(psi)
        return {"status": "success", "message": f"Baseline updated with {len(payload.scores)} scores."}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/status",
    response_model=DriftStatusResponse,
    summary="Get current model drift status",
)
def get_drift_status() -> DriftStatusResponse:
    psi = score_drift_detector.compute_psi()
    
    if psi <= 0.1:
        drift_status = "NO_DRIFT"
    elif psi <= 0.2:
        drift_status = "WARNING"
    else:
        drift_status = "DRIFT"
        
    return DriftStatusResponse(
        psi=psi,
        recent_scores_count=len(score_drift_detector.recent_scores),
        baseline_scores_count=len(score_drift_detector.baseline_scores),
        drift_status=drift_status,
    )
