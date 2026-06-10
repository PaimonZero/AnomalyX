from __future__ import annotations

import sys
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.core.config import get_settings


def _mask_url(url: str) -> str:
    parts = urlsplit(url)
    if "@" not in parts.netloc:
        return url
    _, host = parts.netloc.rsplit("@", 1)
    return urlunsplit((parts.scheme, f"***@{host}", parts.path, parts.query, parts.fragment))


def main() -> int:
    settings = get_settings()
    if settings.alert_repository != "postgres":
        print(f"PostgreSQL check skipped: ALERT_REPOSITORY={settings.alert_repository}.")
        return 0

    try:
        from sqlalchemy import create_engine, inspect, text
    except ModuleNotFoundError:
        print("SQLAlchemy is not installed. Run: pip install -r backend/requirements.txt", file=sys.stderr)
        return 1

    try:
        engine = create_engine(settings.database_url, future=True, pool_pre_ping=True)
        with engine.connect() as connection:
            connection.execute(text("select 1"))
            tables = set(inspect(connection).get_table_names())
    except Exception as exc:
        print(f"PostgreSQL connection failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        print(f"Database URL: {_mask_url(settings.database_url)}", file=sys.stderr)
        return 1

    required_tables = {"alerts", "review_labels", "prediction_logs"}
    missing_tables = sorted(required_tables - tables)
    if missing_tables:
        print(f"PostgreSQL schema check failed. Missing tables: {', '.join(missing_tables)}", file=sys.stderr)
        print("Apply backend/db/schema.sql, then retry.", file=sys.stderr)
        return 1

    print("PostgreSQL reachable: OK")
    print(f"Database URL: {_mask_url(settings.database_url)}")
    print("Required tables: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
