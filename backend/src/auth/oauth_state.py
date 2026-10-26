"""Proteção CSRF do fluxo OAuth via cookie de state assinado e de curta duração.

Evita depender de armazenamento server-side (ver ADR-0005 — MVP sem banco
de dados): o valor é assinado e comparado ao que volta no callback,
seguindo o padrão de "double submit cookie" combinado com expiração. O
state assinado (com o nonce) vai na URL; o cookie guarda só o nonce
aleatório, que precisa casar com o nonce dentro do state.
"""

from __future__ import annotations

import hmac
import uuid

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from ..config import Settings
from ..errors import InvalidOAuthStateError

_SALT = "oauth-state"


def _serializer(settings: Settings) -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(settings.session_secret, salt=_SALT)


def new_login_nonce() -> str:
    """Nonce aleatório (122 bits, os.urandom) do cookie, sem relação com o segredo de assinatura."""
    return uuid.uuid4().hex


def generate_oauth_state(settings: Settings, nonce: str) -> str:
    """State assinado (com o nonce) enviado na URL de autorização."""
    return _serializer(settings).dumps({"nonce": nonce})


def validate_oauth_state(
    settings: Settings, cookie_value: str | None, provided_state: str | None
) -> None:
    if not cookie_value or not provided_state:
        raise InvalidOAuthStateError("Parâmetro state ausente.")
    try:
        payload = _serializer(settings).loads(
            provided_state, max_age=settings.oauth_state_max_age_seconds
        )
    except SignatureExpired as exc:
        raise InvalidOAuthStateError("O state do login expirou.") from exc
    except BadSignature as exc:
        raise InvalidOAuthStateError("O state do login é inválido.") from exc
    nonce = payload.get("nonce") if isinstance(payload, dict) else None
    if not isinstance(nonce, str) or not hmac.compare_digest(cookie_value, nonce):
        raise InvalidOAuthStateError("Parâmetro state não confere com o cookie de origem.")
