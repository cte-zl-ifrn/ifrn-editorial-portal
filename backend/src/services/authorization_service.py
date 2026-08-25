"""Modelo de autorização — ver docs/architecture/authorization-model.md."""

from __future__ import annotations

import httpx

from ..config import Settings
from ..github.app_auth import get_installation_access_token
from ..github.client import get_user_repository_permission

AUTHORIZED_PERMISSIONS = {"write", "maintain", "admin"}


def is_permission_authorized(permission: str) -> bool:
    return permission in AUTHORIZED_PERMISSIONS


def check_user_authorization(
    client: httpx.Client, settings: Settings, username: str
) -> tuple[bool, str]:
    installation_token = get_installation_access_token(client, settings)
    permission = get_user_repository_permission(client, settings, installation_token, username)
    return is_permission_authorized(permission), permission
