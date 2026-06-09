from __future__ import annotations

import sys
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.core.config import get_settings

def _mask_redis_url(url: str) -> str:
    parts = urlsplit(url)
    if "@" not in parts.netloc:
        return url
    creds, host = parts.netloc.rsplit("@", 1)
    user = creds.split(":", 1)[0] if ":" in creds else creds
    safe_netloc = f"{user}:***@{host}" if user else f"***@{host}"
    return urlunsplit((parts.scheme, safe_netloc, parts.path, parts.query, parts.fragment))

def main() -> int:
    try:
        from redis import Redis
    except ModuleNotFoundError:
        print("redis package is not installed. Run: pip install -r backend/requirements.txt")
        return 1

    settings = get_settings()

    redis_url_str = str(settings.redis_url) if settings.redis_url else ""
    if not redis_url_str or not redis_url_str.startswith(("redis://", "rediss://")):
        print("Redis connection failed: redis_url is empty or invalid scheme")
        return 1

    try:
        client = Redis.from_url(redis_url_str, decode_responses=True)
        pong = client.ping()
    except Exception as exc:
        print(f"Redis connection failed: {type(exc).__name__}: {exc}")
        print(f"Redis URL: {_mask_redis_url(redis_url_str)}")
        return 1

    print(f"Redis reachable: {pong}")
    print(f"Redis URL: {_mask_redis_url(redis_url_str)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
