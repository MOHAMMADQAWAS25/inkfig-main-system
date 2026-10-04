from pathlib import Path

from fastapi.testclient import TestClient

from src.infrastructure.config.settings import Settings
from src.lambda_handler import handler
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
    assert Settings.model_fields["database_url"].default == ""
    assert Settings.model_fields["supabase_url"].default == ""
    assert "postgres_host" not in Settings.model_fields


def test_lambda_handler_wraps_fastapi_application() -> None:
    assert callable(handler)


def test_deployment_reuses_user_api_jwt_secret() -> None:
    workflow = Path(".github/workflows/deploy.yml").read_text(encoding="utf-8")

    assert "--function-name inkfig-user-system-api" in workflow
    assert "Environment.Variables.JWT_SECRET" in workflow
    assert 'echo "::add-mask::$JWT_SECRET"' in workflow
    assert "secrets.JWT_SECRET" not in workflow
