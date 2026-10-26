"""Proteção CSRF do fluxo OAuth via cookie de state assinado e de curta duração.

Evita depender de armazenamento server-side (ver ADR-0005 — MVP sem banco
de dados): o valor é assinado e comparado ao que volta no callback,
seguindo o padrão de "double submit cookie" combinado com expiração. O
cookie guarda o HMAC-SHA256 do state (não o state em claro).
"""

from __future__ import annotations

import hashlib
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


def state_cookie_value(settings: Settings, state: str) -> str:
    """Valor gravado no cookie: HMAC-SHA256 do state, nunca o state em claro.

    O state assinado só trafega pela URL de autorização; o cookie guarda
    apenas a impressão digital dele, suficiente para o double submit.
    """
    return hmac.new(
        settings.session_secret.encode("utf-8"),
        f"{_SALT}:{state}".encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def validate_oauth_state(
    settings: Settings, cookie_value: str | None, provided_state: str | None
) -> None:
    if not cookie_value or not provided_state:
        raise InvalidOAuthStateError("Parâmetro state ausente.")
    if not hmac.compare_digest(cookie_value, state_cookie_value(settings, provided_state)):
        raise InvalidOAuthStateError("Parâmetro state não confere com o cookie de origem.")
    try:
        _serializer(settings).loads(
            provided_state, max_age=settings.oauth_state_max_age_seconds
        )
    except SignatureExpired as exc:
        raise InvalidOAuthStateError("O state do login expirou.") from exc
    except BadSignature as exc:
        raise InvalidOAuthStateError("O state do login é inválido.") from exc
