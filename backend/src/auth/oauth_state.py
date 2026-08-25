"""Proteção CSRF do fluxo OAuth via cookie de state assinado e de curta duração.

Evita depender de armazenamento server-side (ver ADR-0005 — MVP sem banco
de dados): o valor é assinado e comparado ao que volta no callback,
seguindo o padrão de "double submit cookie" combinado com expiração.
"""

from __future__ import annotations

import hmac
import secrets

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from ..config import Settings
from ..errors import InvalidOAuthStateError

_SALT = "oauth-state"


def _serializer(settings: Settings) -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(settings.session_secret, salt=_SALT)


def generate_oauth_state(settings: Settings) -> str:
    nonce = secrets.token_urlsafe(16)
    return _serializer(settings).dumps({"nonce": nonce})


def validate_oauth_state(
    settings: Settings, cookie_value: str | None, provided_state: str | None
) -> None:
    if not cookie_value or not provided_state:
        raise InvalidOAuthStateError("Parâmetro state ausente.")
    if not hmac.compare_digest(cookie_value, provided_state):
        raise InvalidOAuthStateError("Parâmetro state não confere com o cookie de origem.")
    try:
        _serializer(settings).loads(
            cookie_value, max_age=settings.oauth_state_max_age_seconds
        )
    except SignatureExpired as exc:
        raise InvalidOAuthStateError("O state do login expirou.") from exc
    except BadSignature as exc:
        raise InvalidOAuthStateError("O state do login é inválido.") from exc
