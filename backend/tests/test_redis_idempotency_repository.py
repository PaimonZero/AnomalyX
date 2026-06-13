from app.core.config import reset_settings_cache
from app.repositories import redis_idempotency_repository


def test_redis_client_uses_configured_timeout_and_retry_settings(monkeypatch) -> None:
    monkeypatch.setenv("REDIS_URL", "redis://cache.example:6379/2")
    monkeypatch.setenv("REDIS_SOCKET_CONNECT_TIMEOUT_SECONDS", "1.5")
    monkeypatch.setenv("REDIS_SOCKET_TIMEOUT_SECONDS", "2.5")
    monkeypatch.setenv("REDIS_RETRY_ON_TIMEOUT", "false")
    monkeypatch.setenv("REDIS_RETRY_ATTEMPTS", "4")
    monkeypatch.setenv("REDIS_RETRY_BACKOFF_BASE_SECONDS", "0.2")
    monkeypatch.setenv("REDIS_RETRY_BACKOFF_CAP_SECONDS", "3.0")
    reset_settings_cache()

    client = object()
    captured: dict[str, object] = {}

    class FakeRedis:
        @staticmethod
        def from_url(url: str, **kwargs):
            captured["url"] = url
            captured["kwargs"] = kwargs
            return client

    monkeypatch.setattr(redis_idempotency_repository, "Redis", FakeRedis)

    repository = redis_idempotency_repository.RedisIdempotencyRepository()

    assert repository.client is client
    assert captured["url"] == "redis://cache.example:6379/2"
    kwargs = captured["kwargs"]
    assert kwargs["decode_responses"] is True
    assert kwargs["socket_connect_timeout"] == 1.5
    assert kwargs["socket_timeout"] == 2.5
    assert kwargs["retry_on_timeout"] is False
    assert kwargs["retry"]._retries == 4
    assert kwargs["retry"]._backoff._base == 0.2
    assert kwargs["retry"]._backoff._cap == 3.0

    reset_settings_cache()
