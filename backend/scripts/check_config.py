from __future__ import annotations

import argparse
import sys
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.core.config import ConfigError, get_settings


def _mask_url(url: str) -> str:
    parts = urlsplit(url)
    if "@" not in parts.netloc:
        return url
    _, host = parts.netloc.rsplit("@", 1)
    return urlunsplit((parts.scheme, f"***@{host}", parts.path, parts.query, parts.fragment))


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate AnomalyX backend settings.")
    parser.add_argument(
        "--runtime",
        action="store_true",
        help="Validate runtime settings. Runtime validation is also run by default settings loading.",
    )
    args = parser.parse_args()

    try:
        settings = get_settings()
        if args.runtime:
            settings.validate_for_runtime()
    except ConfigError as exc:
        print(f"Config error: {exc}", file=sys.stderr)
        return 1

    print("Config loaded successfully.")
    print(f"App: {settings.app_name} ({settings.app_env})")
    print(f"API: {settings.api_host}:{settings.api_port}")
    print(f"OpenAI model: {settings.openai_model}")
    print(f"Mock ML enabled: {settings.mock_ml_enabled}")
    print(
        "Risk thresholds: "
        f"medium={settings.risk_threshold_medium}, flag={settings.risk_threshold_flag}"
    )
    print(f"Alert repository: {settings.alert_repository}")
    print(f"PostgreSQL database URL configured: {bool(settings.database_url)}")
    if settings.database_url:
        print(f"PostgreSQL database URL: {_mask_url(settings.database_url)}")
    print(f"Supabase URL configured: {bool(settings.supabase_url)}")
    print(f"Supabase service role key configured: {bool(settings.supabase_service_role_key)}")
    print(f"Supabase schema: {settings.supabase_schema}")
    print(f"Redis URL configured: {bool(settings.redis_url)}")
    print(f"Idempotency store: {settings.idempotency_store}")
    print(f"Idempotency TTL seconds: {settings.idempotency_ttl_seconds}")
    print(f"OpenAI key configured: {bool(settings.openai_api_key)}")
    print(f"JWT secret configured: {bool(settings.jwt_secret_key)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
