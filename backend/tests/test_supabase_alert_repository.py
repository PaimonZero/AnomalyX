import pytest

from app.repositories.supabase_alert_repository import (
    AlertCreationError,
    SupabaseError,
    SupabaseAlertRepository,
)
from app.schemas.prediction import RiskLevel


def test_create_raises_clear_error_when_supabase_returns_no_rows() -> None:
    repo = SupabaseAlertRepository.__new__(SupabaseAlertRepository)

    def empty_request(*args, **kwargs):
        return []

    repo._request = empty_request

    with pytest.raises(
        AlertCreationError,
        match=r"create\(\).*self\._request.*row_to_alert\(\)",
    ):
        repo.create(
            transaction_id="tx_empty_create_response",
            risk_score=0.91,
            risk_level=RiskLevel.HIGH,
            triggered_rules=[],
            top_features=[],
        )


def test_init_requires_https_supabase_url() -> None:
    with pytest.raises(SupabaseError, match="https URL"):
        SupabaseAlertRepository(
            supabase_url="http://localhost:54321",
            service_role_key="test-service-role-key",
        )


def test_build_table_url_stays_on_supabase_host() -> None:
    repo = SupabaseAlertRepository(
        supabase_url="https://project.supabase.co",
        service_role_key="test-service-role-key",
    )

    assert repo._build_table_url("alerts") == "https://project.supabase.co/rest/v1/alerts"


def test_build_table_url_rejects_host_override() -> None:
    repo = SupabaseAlertRepository(
        supabase_url="https://project.supabase.co",
        service_role_key="test-service-role-key",
    )

    with pytest.raises(SupabaseError, match="must not override"):
        repo._build_table_url("https://evil.example/alerts")

    with pytest.raises(SupabaseError, match="must not override"):
        repo._build_table_url("//evil.example/alerts")
