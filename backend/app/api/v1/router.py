from fastapi import APIRouter
from fastapi import Depends

from app.api.v1.routes import alerts, health, metrics, prediction, rules
from app.api.dependencies.auth import require_api_auth

api_router = APIRouter(prefix="/api/v1")

# Public routers
api_router.include_router(health.router, tags=["health"])
api_router.include_router(metrics.router, tags=["metrics"])

# Protected routers
auth_deps = [Depends(require_api_auth)]
api_router.include_router(prediction.router, tags=["prediction"], dependencies=auth_deps)
api_router.include_router(alerts.router, tags=["alerts"], dependencies=auth_deps)
api_router.include_router(rules.router, tags=["rules"], dependencies=auth_deps)
