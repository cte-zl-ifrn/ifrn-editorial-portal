"""Esquemas de requisição — espelham docs/api/openapi.yaml."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class AssetInput(BaseModel):
    """Um asset a gravar na mesma branch do documento (Fase 3.2, ADR-0007).

    `filename` é sugerido pelo frontend — que precisa referenciá-lo no
    corpo Markdown antes da submissão existir — mas é sempre validado
    pelo backend antes de qualquer gravação (ver src/assets/validation.py).
    O diretório final (`assets/images/{categoria}/` ou
    `assets/files/{categoria}/`) é sempre calculado pelo backend, nunca
    aceito do cliente.
    """

    kind: Literal["image", "file"]
    filename: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1, description="Conteúdo binário em base64.")
    alt: str | None = Field(default=None, max_length=1000)


class SubmissionRequest(BaseModel):
    """`body` é o Markdown já serializado pelo frontend (ver ADR-0009);
    o front matter nunca vem do cliente — o backend relê o documento
    original no momento da gravação (ver ADR-0011)."""

    body: str = Field(..., min_length=1, max_length=200_000)
    base_sha: str = Field(..., min_length=1)
    summary: str = Field(..., min_length=1, max_length=2000)
    assets: list[AssetInput] = Field(default_factory=list, max_length=20)
