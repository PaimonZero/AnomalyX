from fastapi import APIRouter, HTTPException, Query

from app.repositories.alert_repository import AlertNotFoundError
from app.schemas.alert import Alert, AlertStatus, AlertStatusUpdate
from app.services.alert_service import AlertService


router = APIRouter(prefix="/alerts")


@router.get("", response_model=list[Alert])
def list_alerts(status: AlertStatus | None = Query(default=None)) -> list[Alert]:
    return AlertService().list_alerts(status=status)


@router.get("/{alert_id}", response_model=Alert)
def get_alert(alert_id: str) -> Alert:
    try:
        return AlertService().get_alert(alert_id)
    except AlertNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Alert not found.") from exc


@router.patch("/{alert_id}/status", response_model=Alert)
def update_alert_status(alert_id: str, payload: AlertStatusUpdate) -> Alert:
    try:
        return AlertService().update_status(alert_id, payload.status)
    except AlertNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Alert not found.") from exc
