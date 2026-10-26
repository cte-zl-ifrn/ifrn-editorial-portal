"""Leitura do documento de demonstração da Fase 1/2.1 (somente leitura).

O caminho é fixo em `settings.sample_document_path` — não aceita caminho
arbitrário do cliente (ver RF-20 em
docs/requirements/functional-requirements.md).
"""

from __future__ import annotations

import httpx

from ..config import Settings
from ..github.app_auth import get_installation_access_token
from ..github.client import get_repository_content
from ..markdown import split_front_matter
from ..models import DocumentResponse


def read_sample_document(client: httpx.Client, settings: Settings) -> DocumentResponse:
    installation_token = get_installation_access_token(client, settings)
    data = get_repository_content(
        client, settings, installation_token, settings.sample_document_path
    )
    split = split_front_matter(data["content"])
    return DocumentResponse(
        path=data["path"],
        name=data["name"],
        sha=data["sha"],
        front_matter=split.front_matter,
        front_matter_raw=split.front_matter_raw,
        body=split.body,
    )
