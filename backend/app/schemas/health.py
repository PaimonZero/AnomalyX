from datetime import datetime

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    app: str
    environment: str
    timestamp: datetime
    checks: dict[str, bool]
    storage: dict[str, str]
    model: dict[str, str | bool]
    metrics_enabled: bool
