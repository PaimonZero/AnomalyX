from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib import error, parse, request


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.core.config import get_settings


def supabase_request(path: str, query: dict[str, str] | None = None) -> tuple[int, str]:
    settings = get_settings()
    url = f"{settings.supabase_url.rstrip('/')}/rest/v1/{path}"
    if query:
        url = f"{url}?{parse.urlencode(query)}"

    req = request.Request(
        url,
        headers={
            "apikey": settings.supabase_service_role_key,
            "Accept": "application/json",
            "Accept-Profile": settings.supabase_schema,
        },
        method="GET",
    )
    try:
        with request.urlopen(req, timeout=15) as response:
            return response.status, response.read().decode("utf-8", errors="replace")
    except error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", errors="replace")
    except error.URLError as exc:
        return 0, f"Network error: {exc.reason}"


def main() -> int:
    settings = get_settings()
    if settings.alert_repository != "supabase":
        print(f"Supabase check skipped: ALERT_REPOSITORY={settings.alert_repository}.")
        return 0

    if not settings.supabase_url or not settings.supabase_service_role_key:
        print("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY.", file=sys.stderr)
        return 1

    print(f"Supabase URL: {settings.supabase_url.rstrip('/')}")
    print(f"Schema: {settings.supabase_schema}")
    print(f"Service role key configured: {bool(settings.supabase_service_role_key)}")

    status, body = supabase_request("")
    if status != 200:
        print(f"REST root check failed: HTTP {status} {body[:200]}", file=sys.stderr)
        return 1
    print("REST root check: OK")

    status, body = supabase_request("alerts", {"select": "id", "limit": "1"})
    if status == 200:
        try:
            json.loads(body)
        except json.JSONDecodeError:
            print("alerts table check returned non-JSON response.", file=sys.stderr)
            return 1
        print("alerts table check: OK")
        return 0

    print(f"alerts table check failed: HTTP {status} {body[:300]}", file=sys.stderr)
    print("Run supabase/schema.sql in the Supabase SQL Editor, then retry.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
