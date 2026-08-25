import jwt as pyjwt

from src.config import Settings


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
