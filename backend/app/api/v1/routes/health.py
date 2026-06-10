from datetime import datetime, timezone

from fastapi import APIRouter

from app.core.config import get_settings
from app.rules.engine import rule_engine_manager
from app.schemas.health import HealthResponse


router = APIRouter()


def _alert_repository_ready(repository: str) -> bool:
    if repository == "in_memory":
        return True
    if repository == "postgres":
        try:
            from app.repositories.postgres_alert_repository import PostgresAlertRepository

            PostgresAlertRepository().ping()
            return True
        except Exception:
            return False
    if repository == "supabase":
        settings = get_settings()
        return bool(settings.supabase_url and settings.supabase_service_role_key)
    return False


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    settings = get_settings()
    rules_loaded = len(rule_engine_manager.engine.rules) > 0
    alert_repository_ready = _alert_repository_ready(settings.alert_repository)
    checks = {
        "rules_loaded": rules_loaded,
        "model_configured": settings.mock_ml_enabled,
        "idempotency_configured": settings.idempotency_store in {"in_memory", "redis"},
        "alert_repository_configured": settings.alert_repository in {"in_memory", "postgres", "supabase"},
        "alert_repository_ready": alert_repository_ready,
    }
    return HealthResponse(
        status="ok" if all(checks.values()) else "degraded",
        app=settings.app_name,
        environment=settings.app_env,
        timestamp=datetime.now(timezone.utc),
        checks=checks,
        storage={
            "alert_repository": settings.alert_repository,
            "idempotency_store": settings.idempotency_store,
        },
        model={
            "mock_enabled": settings.mock_ml_enabled,
            "version": "mock-ml-v1" if settings.mock_ml_enabled else "external",
        },
        metrics_enabled=settings.metrics_enabled,
    )
