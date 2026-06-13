from __future__ import annotations

from urllib.parse import urlsplit, urlunsplit


def _mask_url(url: str) -> str:
    parts = urlsplit(url)
    if "@" not in parts.netloc:
        return url
    _, host = parts.netloc.rsplit("@", 1)
    return urlunsplit((parts.scheme, f"***@{host}", parts.path, parts.query, parts.fragment))
