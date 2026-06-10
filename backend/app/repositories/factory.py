from __future__ import annotations

from functools import lru_cache

from app.core.config import get_settings
from app.repositories.alert_repository import AlertRepository, InMemoryAlertRepository
from app.repositories.supabase_alert_repository import SupabaseAlertRepository


@lru_cache(maxsize=1)
def get_alert_repository() -> AlertRepository:
    settings = get_settings()
    if settings.alert_repository == "postgres":
        from app.repositories.postgres_alert_repository import PostgresAlertRepository

        return PostgresAlertRepository()
    if settings.alert_repository == "supabase":
        return SupabaseAlertRepository()
    if settings.alert_repository == "in_memory":
        return InMemoryAlertRepository()

    raise ValueError("ALERT_REPOSITORY must be one of: in_memory, postgres, supabase.")


def reset_alert_repository_cache() -> None:
    get_alert_repository.cache_clear()
