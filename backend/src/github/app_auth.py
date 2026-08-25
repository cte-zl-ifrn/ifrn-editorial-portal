"""Identidade técnica da GitHub App: JWT da aplicação e installation access token.

Distinto da autenticação da pessoa usuária (OAuth) — ver
docs/architecture/authentication-flow.md. Nesta fase, a instalação usada
tem apenas permissões Contents:Read-only e Metadata:Read-only (ver
docs/decisions/0004-integracao-github-app.md e docs/phase-1-plan.md).
"""

from __future__ import annotations

import time

import httpx
import jwt

from ..config import Settings
from ..errors import GithubCommunicationError, MissingConfigurationError


def build_app_jwt(settings: Settings, *, now: int | None = None) -> str:
    if not settings.github_app_id or not settings.github_app_private_key:
        raise MissingConfigurationError(
            "Credenciais da GitHub App não configuradas (github_app_id / github_app_private_key)."
        )
    issued_at = now if now is not None else int(time.time())
    payload = {
        "iat": issued_at - 60,
        "exp": issued_at + 9 * 60,
        "iss": settings.github_app_id,
    }
    return jwt.encode(payload, settings.github_app_private_key, algorithm="RS256")


def get_installation_id(client: httpx.Client, settings: Settings, app_jwt: str) -> str:
    if settings.github_app_installation_id:
        return settings.github_app_installation_id
    url = (
        f"{settings.github_api_base_url}/repos/"
        f"{settings.github_owner}/{settings.github_repository}/installation"
    )
    response = client.get(
        url,
        headers={
            "Authorization": f"Bearer {app_jwt}",
            "Accept": "application/vnd.github+json",
        },
    )
    if response.status_code != 200:
        raise GithubCommunicationError(
            "Não foi possível localizar a instalação da GitHub App no repositório."
        )
    return str(response.json()["id"])


def get_installation_access_token(client: httpx.Client, settings: Settings) -> str:
    app_jwt = build_app_jwt(settings)
    installation_id = get_installation_id(client, settings, app_jwt)
    url = f"{settings.github_api_base_url}/app/installations/{installation_id}/access_tokens"
    response = client.post(
        url,
        headers={
            "Authorization": f"Bearer {app_jwt}",
            "Accept": "application/vnd.github+json",
        },
    )
    if response.status_code != 201:
        raise GithubCommunicationError(
            "Não foi possível obter o installation access token da GitHub App."
        )
    return str(response.json()["token"])
