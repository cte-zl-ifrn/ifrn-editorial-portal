"""Esquemas de resposta da API — espelham docs/api/openapi.yaml."""

from __future__ import annotations

from typing import Any

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
    """Ver ADR-0009: front_matter_raw + body reproduz o arquivo original;
    front_matter é o mesmo conteúdo já parseado, apenas para exibição."""

    path: str
    name: str
    sha: str
    front_matter: dict[str, Any]
    front_matter_raw: str
    body: str


class PullRequestInfo(BaseModel):
    number: int
    html_url: str
    state: str


class SubmissionResponse(BaseModel):
    submission_id: str
    branch: str
    pull_request: PullRequestInfo


class ErrorResponse(BaseModel):
    error: str
    message: str | None = None
    correlation_id: str | None = None
