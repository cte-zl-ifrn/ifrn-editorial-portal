import json
from unittest.mock import patch

import jwt as pyjwt
import pytest

from src.config import SECRETS_MANAGER_SECRET_ARN_ENV_VAR, Settings, get_settings


def test_private_key_with_real_newlines_is_kept_usable(test_private_key_pem):
    settings = Settings(github_app_private_key=test_private_key_pem)

    assert settings.github_app_private_key.count("\n") == test_private_key_pem.count("\n")
    # Deve continuar utilizável para assinar um JWT.
    pyjwt.encode({"iss": "1"}, settings.github_app_private_key, algorithm="RS256")


def test_private_key_pasted_with_escaped_newlines_is_normalized(test_private_key_pem):
    """Reproduz o bug relatado: colar o .pem em uma única linha, com `\n`
    literal em vez de quebra de linha real, quebrava o carregamento do PEM
    (jwt.exceptions.InvalidKeyError: Could not parse the provided public
    key.)."""
    escaped = test_private_key_pem.strip().replace("\n", "\\n")
    assert "\\n" in escaped
    assert "\n" not in escaped

    settings = Settings(github_app_private_key=escaped)

    assert "\\n" not in settings.github_app_private_key
    pyjwt.encode({"iss": "1"}, settings.github_app_private_key, algorithm="RS256")


def test_private_key_wrapped_in_quotes_is_normalized(test_private_key_pem):
    escaped = test_private_key_pem.strip().replace("\n", "\\n")
    quoted = f'"{escaped}"'

    settings = Settings(github_app_private_key=quoted)

    assert not settings.github_app_private_key.startswith('"')
    pyjwt.encode({"iss": "1"}, settings.github_app_private_key, algorithm="RS256")


def test_empty_private_key_stays_empty():
    settings = Settings(github_app_private_key="")
    assert settings.github_app_private_key == ""


@pytest.fixture
def _clear_settings_cache():
    """`get_settings()` é cacheado (`lru_cache`); sem limpar o cache entre
    testes, o primeiro resultado calculado "vazaria" para os demais."""
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_get_settings_uses_env_when_secrets_manager_arn_is_absent(
    monkeypatch, _clear_settings_cache
):
    """Sem a variável do ARN (desenvolvimento local), o comportamento é
    idêntico ao anterior à Fase 4.1 — ver ADR-0012."""
    monkeypatch.delenv(SECRETS_MANAGER_SECRET_ARN_ENV_VAR, raising=False)
    monkeypatch.setenv("SESSION_SECRET", "from-env")

    settings = get_settings()

    assert settings.session_secret == "from-env"


def test_get_settings_loads_overrides_from_secrets_manager_when_arn_is_present(
    monkeypatch, _clear_settings_cache, test_private_key_pem
):
    monkeypatch.setenv(SECRETS_MANAGER_SECRET_ARN_ENV_VAR, "arn:secret:portal")
    secret_payload = {
        "GITHUB_OAUTH_CLIENT_SECRET": "secret-from-sm",
        "GITHUB_APP_ID": "99999",
        "GITHUB_APP_PRIVATE_KEY": test_private_key_pem,
        "SESSION_SECRET": "session-secret-from-sm",
    }

    with patch("src.config.boto3.client") as mock_client_factory:
        mock_client = mock_client_factory.return_value
        mock_client.get_secret_value.return_value = {"SecretString": json.dumps(secret_payload)}

        settings = get_settings()

    mock_client_factory.assert_called_once_with("secretsmanager")
    mock_client.get_secret_value.assert_called_once_with(
        SecretId="arn:secret:portal"
    )
    assert settings.github_oauth_client_secret == "secret-from-sm"
    assert settings.github_app_id == "99999"
    assert settings.session_secret == "session-secret-from-sm"


def test_get_settings_fails_loudly_when_secrets_manager_fetch_fails(
    monkeypatch, _clear_settings_cache
):
    """Falha ao buscar o segredo nunca deve cair silenciosamente nos
    valores padrão inseguros de `Settings` — ver ADR-0012."""
    monkeypatch.setenv(SECRETS_MANAGER_SECRET_ARN_ENV_VAR, "arn:secret:portal")

    with patch("src.config.boto3.client") as mock_client_factory:
        mock_client_factory.return_value.get_secret_value.side_effect = RuntimeError("boom")

        with pytest.raises(RuntimeError):
            get_settings()


def test_get_settings_fails_loudly_when_secret_payload_is_missing_a_key(
    monkeypatch, _clear_settings_cache
):
    monkeypatch.setenv(SECRETS_MANAGER_SECRET_ARN_ENV_VAR, "arn:secret:portal")
    incomplete_payload = {"GITHUB_OAUTH_CLIENT_SECRET": "x"}  # faltam as outras 3 chaves

    with patch("src.config.boto3.client") as mock_client_factory:
        mock_client_factory.return_value.get_secret_value.return_value = {
            "SecretString": json.dumps(incomplete_payload)
        }

        with pytest.raises(KeyError):
            get_settings()
