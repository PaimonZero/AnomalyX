from __future__ import annotations

import sys
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.core.config import get_settings


def main() -> int:
    try:
        from redis import Redis
    except ModuleNotFoundError:
        print("redis package is not installed. Run: pip install -r backend/requirements.txt")
        return 1

    settings = get_settings()
    client = Redis.from_url(settings.redis_url, decode_responses=True)
    try:
        pong = client.ping()
    except Exception as exc:
        print(f"Redis connection failed: {type(exc).__name__}: {exc}")
        print(f"Redis URL: {settings.redis_url}")
        return 1

    print(f"Redis reachable: {pong}")
    print(f"Redis URL: {settings.redis_url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
