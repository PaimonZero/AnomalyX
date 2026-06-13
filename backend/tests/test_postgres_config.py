import importlib.util
import os

import pytest

from app.core.config import ConfigError, _load_dotenv, get_settings, reset_settings_cache
from app.repositories.factory import get_alert_repository, reset_alert_repository_cache


_ENV_KEYS = [
    "AUTH_TOKEN",
    "JWT_SECRET_KEY",
    "ALERT_REPOSITORY",
    "DATABASE_URL",
    "POSTGRES_HOST",
    "POSTGRES_PORT",
    "POSTGRES_DB",
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
    "POSTGRES_SSLMODE",
    "SUPABASE_URL",
    "SUPABASE_SERVICE_ROLE_KEY",
]


@pytest.fixture
def clean_settings(monkeypatch: pytest.MonkeyPatch):
    for key in _ENV_KEYS:
        monkeypatch.setenv(key, "")
    monkeypatch.setenv("AUTH_TOKEN", "test-service-token-strong-000000000000")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-jwt-secret-strong-000000000000")
    reset_settings_cache()
    reset_alert_repository_cache()
    yield
    reset_settings_cache()
    reset_alert_repository_cache()


def test_in_memory_config_does_not_require_external_database(clean_settings, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ALERT_REPOSITORY", "in_memory")
    reset_settings_cache()

    settings = get_settings()

    assert settings.alert_repository == "in_memory"


def test_load_dotenv_preserves_intentionally_empty_env(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("OPENAI_API_KEY=from-dotenv\n", encoding="utf-8")
    monkeypatch.setenv("OPENAI_API_KEY", "")
    _load_dotenv.cache_clear()

    _load_dotenv(env_file)

    assert "OPENAI_API_KEY" in os.environ
    assert os.environ["OPENAI_API_KEY"] == ""


def test_postgres_config_accepts_database_url_without_supabase(clean_settings, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ALERT_REPOSITORY", "postgres")
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://user:pass@localhost:5432/anomalyx")
    reset_settings_cache()

    settings = get_settings()

    assert settings.alert_repository == "postgres"
    assert settings.database_url == "postgresql+psycopg://user:pass@localhost:5432/anomalyx"


def test_postgres_config_can_build_url_from_parts(clean_settings, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ALERT_REPOSITORY", "postgres")
    monkeypatch.setenv("POSTGRES_HOST", "localhost")
    monkeypatch.setenv("POSTGRES_PORT", "5432")
    monkeypatch.setenv("POSTGRES_DB", "anomalyx")
    monkeypatch.setenv("POSTGRES_USER", "anomalyx_user")
    monkeypatch.setenv("POSTGRES_PASSWORD", "anomalyx_password")
    monkeypatch.setenv("POSTGRES_SSLMODE", "disable")
    reset_settings_cache()

    settings = get_settings()

    assert settings.database_url.startswith("postgresql+psycopg://anomalyx_user:")
    assert "localhost:5432/anomalyx" in settings.database_url


def test_postgres_config_requires_url_or_password(clean_settings, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ALERT_REPOSITORY", "postgres")
    monkeypatch.setenv("DATABASE_URL", " ")
    reset_settings_cache()

    with pytest.raises(ConfigError, match="DATABASE_URL"):
        get_settings()


def test_supabase_config_requires_supabase_credentials(clean_settings, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ALERT_REPOSITORY", "supabase")
    monkeypatch.setenv("SUPABASE_URL", " ")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", " ")
    reset_settings_cache()

    with pytest.raises(ConfigError, match="SUPABASE_URL"):
        get_settings()


def test_factory_selects_postgres_repository(clean_settings, monkeypatch: pytest.MonkeyPatch) -> None:
    if importlib.util.find_spec("sqlalchemy") is None or importlib.util.find_spec("psycopg") is None:
        pytest.skip("PostgreSQL dependencies are not installed in this environment")

    monkeypatch.setenv("ALERT_REPOSITORY", "postgres")
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://user:pass@localhost:5432/anomalyx")
    reset_settings_cache()
    reset_alert_repository_cache()

    from app.repositories.postgres_alert_repository import PostgresAlertRepository

    repository = get_alert_repository()

    assert isinstance(repository, PostgresAlertRepository)
