from fastapi.testclient import TestClient

from src.infrastructure.config.settings import Settings
from src.main import create_app


def test_versioned_health_check() -> None:
    response = TestClient(create_app()).get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {
        "service": "inkfig-main-system",
        "status": "ok",
        "environment": "local",
    }


def test_root_health_check() -> None:
    response = TestClient(create_app()).get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_settings_use_supabase_database_url_without_local_fallback() -> None:
    settings = Settings()

    assert settings.database_url == ""
    assert settings.supabase_url == ""
    assert not hasattr(settings, "postgres_host")
