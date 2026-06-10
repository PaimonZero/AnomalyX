from collections.abc import Iterator
import os

import pytest

os.environ.setdefault("AUTH_TOKEN", "test-service-token")
os.environ.setdefault("JWT_SECRET_KEY", "test-jwt-secret")
os.environ.setdefault("ALERT_REPOSITORY", "in_memory")
os.environ.setdefault("IDEMPOTENCY_STORE", "in_memory")

from app.llm.explainer import ExplanationResult, OpenAIAlertExplainer
from app.repositories.idempotency_repository import idempotency_repository
from app.repositories.alert_repository import alert_repository
from app.schemas.alert import Alert
from app.schemas.prediction import TransactionRequest
from app.main import app
from app.api.dependencies.auth import require_api_auth

@pytest.fixture(autouse=True)
def override_auth_dependency() -> Iterator[None]:
    app.dependency_overrides[require_api_auth] = lambda: "test_key"
    yield
    app.dependency_overrides.pop(require_api_auth, None)

@pytest.fixture
def disable_real_openai_calls(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    def fake_explain(
        self: OpenAIAlertExplainer,
        alert: Alert,
        transaction: TransactionRequest,
    ) -> ExplanationResult:
        return ExplanationResult(
            text=f"Test explanation for {alert.id}",
            source="template",
        )

    monkeypatch.setattr(OpenAIAlertExplainer, "explain", fake_explain)
    yield


@pytest.fixture(autouse=True)
def use_in_memory_alert_repository(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    alert_repository.clear()
    monkeypatch.setattr(
        "app.services.alert_service.get_alert_repository",
        lambda: alert_repository,
    )
    yield
    alert_repository.clear()


@pytest.fixture(autouse=True)
def use_in_memory_idempotency_repository(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    idempotency_repository.clear()
    monkeypatch.setattr(
        "app.services.idempotency_service.get_idempotency_repository",
        lambda: idempotency_repository,
    )
    yield
    idempotency_repository.clear()
