"""Esquemas de resposta da API — espelham docs/api/openapi.yaml."""

from __future__ import annotations

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str = "ok"


class GithubUser(BaseModel):
    login: str
    name: str | None = None
    avatar_url: str | None = None


class MeResponse(BaseModel):
    user: GithubUser
    authorized: bool
    repository_permission: str | None = None


class DocumentResponse(BaseModel):
    path: str
    name: str
    content: str
    sha: str
    encoding: str = "utf-8"


class ErrorResponse(BaseModel):
    error: str
    message: str | None = None
    correlation_id: str | None = None
