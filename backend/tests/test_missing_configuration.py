from conftest import set_session_cookie

from src.app import app
from src.config import get_settings


def test_missing_github_app_credentials_returns_500(client, settings):
    incomplete_settings = settings.model_copy(
        update={"github_app_id": "", "github_app_private_key": ""}
    )
    app.dependency_overrides[get_settings] = lambda: incomplete_settings
    set_session_cookie(client, incomplete_settings, authorized=True, permission="write")

    response = client.get("/api/documents/sample")

    assert response.status_code == 500
    assert response.json()["error"] == "missing_configuration"
