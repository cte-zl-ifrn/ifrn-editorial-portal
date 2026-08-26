"""Esquemas de requisição — espelham docs/api/openapi.yaml."""

from __future__ import annotations

from pydantic import BaseModel, Field


class SubmissionRequest(BaseModel):
    """`body` é o Markdown já serializado pelo frontend (ver ADR-0009);
    o front matter nunca vem do cliente — o backend relê o documento
    original no momento da gravação (ver ADR-0011)."""

    body: str = Field(..., min_length=1, max_length=200_000)
    base_sha: str = Field(..., min_length=1)
    summary: str = Field(..., min_length=1, max_length=2000)
