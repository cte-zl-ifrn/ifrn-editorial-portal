from __future__ import annotations

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient

from src.app import app
from src.auth.session import create_session_cookie_value
from src.config import Settings, get_settings


@pytest.fixture(scope="session")
def test_private_key_pem() -> str:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    return pem.decode("utf-8")


@pytest.fixture
def settings(test_private_key_pem: str) -> Settings:
    return Settings(
        github_owner="cte-zl-ifrn",
        github_repository="central-ajuda",
        github_base_branch="main",
        sample_document_path="_docs/proitec/como-fazer-cursos.md",
        github_oauth_client_id="test-client-id",
        github_oauth_client_secret="test-client-secret",
        github_oauth_redirect_uri="http://localhost:8000/auth/callback",
        github_app_id="12345",
        github_app_private_key=test_private_key_pem,
        github_app_installation_id="999",
        session_secret="test-session-secret",
        frontend_url="http://localhost:5173",
        cookie_secure=False,
        cookie_samesite="lax",
    )


@pytest.fixture
def client(settings: Settings):
    app.dependency_overrides[get_settings] = lambda: settings
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def set_session_cookie(
    client: TestClient,
    settings: Settings,
    *,
    login: str = "maria.silva",
    authorized: bool = True,
    permission: str = "write",
) -> None:
    cookie_value = create_session_cookie_value(
        settings,
        {
            "login": login,
            "name": "Maria Silva",
            "avatar_url": "https://x/a.png",
            "authorized": authorized,
            "repository_permission": permission,
        },
    )
    client.cookies.set(settings.session_cookie_name, cookie_value)
