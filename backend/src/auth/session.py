"""Sessão do portal: cookie assinado, HttpOnly, sem armazenamento server-side.

Distinta da identidade técnica da GitHub App — ver
docs/architecture/authentication-flow.md.
"""

from __future__ import annotations

from typing import TypedDict

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from ..config import Settings

_SALT = "portal-session"


class SessionData(TypedDict):
    login: str
    name: str | None
    avatar_url: str | None
    authorized: bool
    repository_permission: str | None


def _serializer(settings: Settings) -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(settings.session_secret, salt=_SALT)


def create_session_cookie_value(settings: Settings, data: SessionData) -> str:
    return _serializer(settings).dumps(dict(data))


def read_session(settings: Settings, cookie_value: str | None) -> SessionData | None:
    if not cookie_value:
        return None
    try:
        payload = _serializer(settings).loads(
            cookie_value, max_age=settings.session_max_age_seconds
        )
    except (BadSignature, SignatureExpired):
        return None
    return payload  # type: ignore[return-value]
