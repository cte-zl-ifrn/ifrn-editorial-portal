"""Orquestra o fluxo OAuth (login/callback) — ver
docs/architecture/authentication-flow.md."""

from __future__ import annotations

from urllib.parse import urlencode

import httpx

from ..auth.oauth_state import generate_oauth_state, validate_oauth_state
from ..auth.session import SessionData
from ..config import Settings
from ..github.client import exchange_code_for_token, get_authenticated_user
from .authorization_service import check_user_authorization


def build_authorize_url(settings: Settings) -> tuple[str, str]:
    """Retorna (url_de_autorizacao, state_assinado)."""
    state = generate_oauth_state(settings)
    params = {
        "client_id": settings.github_oauth_client_id,
        "redirect_uri": settings.github_oauth_redirect_uri,
        "state": state,
        "allow_signup": "false",
    }
    url = f"{settings.github_oauth_base_url}/login/oauth/authorize?{urlencode(params)}"
    return url, state


def complete_login(
    client: httpx.Client,
    settings: Settings,
    *,
    code: str,
    state: str,
    state_cookie_value: str | None,
) -> SessionData:
    validate_oauth_state(settings, state_cookie_value, state)

    user_token = exchange_code_for_token(client, settings, code)
    profile = get_authenticated_user(client, settings, user_token)
    login = profile["login"]

    authorized, permission = check_user_authorization(client, settings, login)

    return SessionData(
        login=login,
        name=profile.get("name"),
        avatar_url=profile.get("avatar_url"),
        authorized=authorized,
        repository_permission=permission,
    )
