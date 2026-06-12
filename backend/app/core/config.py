from __future__ import annotations

import os
from functools import lru_cache
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote_plus


PROJECT_ROOT = Path(__file__).resolve().parents[3]
ENV_FILE = PROJECT_ROOT / ".env"


class ConfigError(ValueError):
    """Raised when runtime configuration is invalid."""


@lru_cache(maxsize=1)
def _load_dotenv(path: Path = ENV_FILE) -> None:
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key not in os.environ or os.environ[key] == "":
            os.environ[key] = value


def _get_bool(name: str, default: bool) -> bool:
    raw_value = os.getenv(name)
    if raw_value is None or raw_value == "":
        return default

    normalized = raw_value.strip().lower()
    if normalized in {"1", "true", "yes", "y", "on"}:
        return True
    if normalized in {"0", "false", "no", "n", "off"}:
        return False

    raise ConfigError(f"{name} must be a boolean value.")


def _get_int(name: str, default: int) -> int:
    raw_value = os.getenv(name)
    if raw_value is None or raw_value == "":
        return default

    try:
        return int(raw_value)
    except ValueError as exc:
        raise ConfigError(f"{name} must be an integer.") from exc


def _get_float(name: str, default: float) -> float:
    raw_value = os.getenv(name)
    if raw_value is None or raw_value == "":
        return default

    try:
        return float(raw_value)
    except ValueError as exc:
        raise ConfigError(f"{name} must be a number.") from exc


def _build_database_url(
    host: str,
    port: int,
    database: str,
    user: str,
    password: str,
    sslmode: str,
) -> str:
    if not all([host, database, user, password]):
        return ""

    url = (
        "postgresql+psycopg://"
        f"{quote_plus(user)}:{quote_plus(password)}@{host}:{port}/{quote_plus(database)}"
    )
    if sslmode:
        url = f"{url}?sslmode={quote_plus(sslmode)}"
    return url


@dataclass(frozen=True)
class Settings:
    app_env: str
    app_name: str
    api_host: str
    api_port: int
    openai_api_key: str
    openai_model: str
    openai_explanation_language: str
    mock_ml_enabled: bool
    mock_ml_seed: int
    risk_threshold_medium: float
    risk_threshold_flag: float
    auth_token: str
    supabase_url: str
    supabase_service_role_key: str
    supabase_schema: str
    alert_repository: str
    postgres_host: str
    postgres_port: int
    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_sslmode: str
    database_url: str
    redis_url: str
    redis_socket_connect_timeout_seconds: float
    redis_socket_timeout_seconds: float
    redis_retry_on_timeout: bool
    redis_retry_attempts: int
    redis_retry_backoff_base_seconds: float
    redis_retry_backoff_cap_seconds: float
    idempotency_store: str
    idempotency_ttl_seconds: int
    jwt_secret_key: str
    jwt_algorithm: str
    access_token_expire_minutes: int
    log_level: str
    metrics_enabled: bool
    model_path: str
    model_config_path: str

    def validate_for_runtime(self) -> None:
        missing = []
        if not self.jwt_secret_key:
            missing.append("JWT_SECRET_KEY")
        if not self.auth_token:
            missing.append("AUTH_TOKEN")
        if missing:
            joined = ", ".join(missing)
            raise ConfigError(f"Missing required runtime secret(s): {joined}.")

        insecure = []
        known_dev_values = {
            "dev-service-token",
            "dev-jwt-secret",
            "test-service-token",
            "test-jwt-secret",
            "changeme",
            "change-me",
            "secret",
            "password",
        }
        secret_requirements = {
            "JWT_SECRET_KEY": self.jwt_secret_key,
            "AUTH_TOKEN": self.auth_token,
        }
        for name, value in secret_requirements.items():
            normalized = value.strip().lower()
            reasons = []
            if normalized in known_dev_values:
                reasons.append("uses a known dev/default value")
            if len(value.strip()) < 32:
                reasons.append("must be at least 32 characters")
            if reasons:
                insecure.append(f"{name} ({'; '.join(reasons)})")
        if insecure:
            joined = ", ".join(insecure)
            raise ConfigError(f"Insecure runtime secret(s): {joined}.")

        if self.alert_repository not in {"in_memory", "postgres", "supabase"}:
            raise ConfigError("ALERT_REPOSITORY must be one of: in_memory, postgres, supabase.")

        if self.alert_repository == "postgres" and not self.database_url.strip():
            raise ConfigError(
                "DATABASE_URL or POSTGRES_HOST/POSTGRES_DB/POSTGRES_USER/POSTGRES_PASSWORD "
                "is required when ALERT_REPOSITORY=postgres."
            )

        if self.alert_repository == "supabase" and (
            not self.supabase_url.strip() or not self.supabase_service_role_key.strip()
        ):
            raise ConfigError(
                "SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are required "
                "when ALERT_REPOSITORY=supabase."
            )

        if not 0 <= self.risk_threshold_medium < self.risk_threshold_flag <= 1:
            raise ConfigError(
                "Risk thresholds must satisfy "
                "0 <= RISK_THRESHOLD_MEDIUM < RISK_THRESHOLD_FLAG <= 1."
            )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    _load_dotenv()

    postgres_host = os.getenv("POSTGRES_HOST", "localhost")
    postgres_port = _get_int("POSTGRES_PORT", 5432)
    postgres_db = os.getenv("POSTGRES_DB", "anomalyx")
    postgres_user = os.getenv("POSTGRES_USER", "anomalyx_user")
    postgres_password = os.getenv("POSTGRES_PASSWORD", "")
    postgres_sslmode = os.getenv("POSTGRES_SSLMODE", "disable")
    database_url = os.getenv("DATABASE_URL", "") or _build_database_url(
        host=postgres_host,
        port=postgres_port,
        database=postgres_db,
        user=postgres_user,
        password=postgres_password,
        sslmode=postgres_sslmode,
    )

    settings = Settings(
        app_env=os.getenv("APP_ENV", "development"),
        app_name=os.getenv("APP_NAME", "AnomalyX"),
        api_host=os.getenv("API_HOST", "127.0.0.1"),
        api_port=_get_int("API_PORT", 8000),
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        openai_explanation_language=os.getenv("OPENAI_EXPLANATION_LANGUAGE", "vi,en"),
        mock_ml_enabled=_get_bool("MOCK_ML_ENABLED", True),
        mock_ml_seed=_get_int("MOCK_ML_SEED", 42),
        risk_threshold_medium=_get_float("RISK_THRESHOLD_MEDIUM", 0.40),
        risk_threshold_flag=_get_float(
            "RISK_THRESHOLD_FLAG",
            _get_float("RISK_THRESHOLD_HIGH", 0.70),
        ),
        auth_token=os.getenv("AUTH_TOKEN", ""),
        supabase_url=os.getenv("SUPABASE_URL", ""),
        supabase_service_role_key=os.getenv("SUPABASE_SERVICE_ROLE_KEY", ""),
        supabase_schema=os.getenv("SUPABASE_SCHEMA", "public"),
        alert_repository=os.getenv("ALERT_REPOSITORY", "in_memory"),
        postgres_host=postgres_host,
        postgres_port=postgres_port,
        postgres_db=postgres_db,
        postgres_user=postgres_user,
        postgres_password=postgres_password,
        postgres_sslmode=postgres_sslmode,
        database_url=database_url,
        redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
        redis_socket_connect_timeout_seconds=_get_float("REDIS_SOCKET_CONNECT_TIMEOUT_SECONDS", 2.0),
        redis_socket_timeout_seconds=_get_float("REDIS_SOCKET_TIMEOUT_SECONDS", 2.0),
        redis_retry_on_timeout=_get_bool("REDIS_RETRY_ON_TIMEOUT", True),
        redis_retry_attempts=_get_int("REDIS_RETRY_ATTEMPTS", 2),
        redis_retry_backoff_base_seconds=_get_float("REDIS_RETRY_BACKOFF_BASE_SECONDS", 0.05),
        redis_retry_backoff_cap_seconds=_get_float("REDIS_RETRY_BACKOFF_CAP_SECONDS", 0.5),
        idempotency_store=os.getenv("IDEMPOTENCY_STORE", "in_memory"),
        idempotency_ttl_seconds=_get_int("IDEMPOTENCY_TTL_SECONDS", 86400),
        jwt_secret_key=os.getenv("JWT_SECRET_KEY", ""),
        jwt_algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
        access_token_expire_minutes=_get_int("ACCESS_TOKEN_EXPIRE_MINUTES", 60),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        metrics_enabled=_get_bool("METRICS_ENABLED", True),
        model_path=os.getenv("MODEL_PATH", "ml/models/artifacts/xgb_aml_v1.json"),
        model_config_path=os.getenv(
            "MODEL_CONFIG_PATH", "ml/models/artifacts/model_config.json"
        ),
    )

    settings.validate_for_runtime()
    return settings


def reset_settings_cache() -> None:
    get_settings.cache_clear()
    _load_dotenv.cache_clear()
