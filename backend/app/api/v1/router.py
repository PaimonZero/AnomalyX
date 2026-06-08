from fastapi import APIRouter

from app.api.v1.routes import alerts, health, metrics, prediction, rules


api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health.router, tags=["health"])
api_router.include_router(metrics.router, tags=["metrics"])
api_router.include_router(prediction.router, tags=["prediction"])
api_router.include_router(alerts.router, tags=["alerts"])
api_router.include_router(rules.router, tags=["rules"])
