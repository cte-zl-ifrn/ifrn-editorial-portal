"""Dependências compartilhadas do FastAPI (config, cliente HTTP, sessão)."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Annotated

import httpx
from fastapi import Depends, Request

from .auth.session import SessionData, read_session
from .config import Settings, get_settings
from .errors import NotAuthenticatedError, NotAuthorizedError


def get_http_client() -> Iterator[httpx.Client]:
    with httpx.Client(timeout=10.0) as client:
        yield client


SettingsDep = Annotated[Settings, Depends(get_settings)]
HttpClientDep = Annotated[httpx.Client, Depends(get_http_client)]


def get_current_session(request: Request, settings: SettingsDep) -> SessionData:
    cookie_value = request.cookies.get(settings.session_cookie_name)
    session = read_session(settings, cookie_value)
    if session is None:
        raise NotAuthenticatedError("Sessão ausente, inválida ou expirada.")
    return session


CurrentSessionDep = Annotated[SessionData, Depends(get_current_session)]


def require_authorized_session(session: CurrentSessionDep) -> SessionData:
    if not session["authorized"]:
        raise NotAuthorizedError(
            "Usuário autenticado, mas sem permissão suficiente no repositório."
        )
    return session


AuthorizedSessionDep = Annotated[SessionData, Depends(require_authorized_session)]
