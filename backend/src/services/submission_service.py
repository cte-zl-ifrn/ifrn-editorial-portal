"""Escrita de um documento no central-ajuda: branch, commit e Pull Request
(Fase 3.1).

Ver ADR-0011: o backend relê o documento imediatamente antes de gravar e
compara com `base_sha` (conflito de edição concorrente); o front matter
sempre vem dessa releitura, nunca do que o cliente enviou; a gravação usa
chamadas sequenciais à Contents API, não a Git Data API.
"""

from __future__ import annotations

import secrets
from datetime import UTC, datetime

import httpx

from ..auth.session import SessionData
from ..config import Settings
from ..errors import DocumentConflictError
from ..github.app_auth import get_installation_access_token
from ..github.client import (
    create_branch,
    create_pull_request,
    get_main_branch_sha,
    get_repository_content,
    update_file_content,
)
from ..markdown import split_front_matter
from ..models import PullRequestInfo, SubmissionResponse
from ..models.requests import SubmissionRequest


def _slug_from_path(path: str) -> str:
    name = path.rsplit("/", 1)[-1]
    return name.removesuffix(".md")


def _build_pull_request_body(*, summary: str, author: str, path: str) -> str:
    now = datetime.now(UTC).isoformat()
    return (
        "## Alteração proposta\n\n"
        f"{summary}\n\n"
        "## Autor da solicitação\n\n"
        f"- Usuário: @{author}\n"
        f"- Data: {now}\n"
        "- Origem: ifrn-editorial-portal\n\n"
        "## Arquivos alterados\n\n"
        f"- `{path}`\n\n"
        "## Validações\n\n"
        "- [ ] Markdown válido\n"
        "- [ ] Front matter válido\n"
        "- [ ] Links verificados\n"
        "- [ ] Texto alternativo informado para imagens\n"
        "- [ ] Revisão institucional\n"
    )


def submit_document(
    client: httpx.Client,
    settings: Settings,
    request: SubmissionRequest,
    session: SessionData,
) -> SubmissionResponse:
    installation_token = get_installation_access_token(client, settings)
    path = settings.sample_document_path

    current = get_repository_content(client, settings, installation_token, path)
    if current["sha"] != request.base_sha:
        raise DocumentConflictError(
            "O documento foi alterado no repositório desde que você começou a editar."
        )

    front_matter_split = split_front_matter(current["content"])
    new_content = front_matter_split.front_matter_raw + request.body

    base_sha = get_main_branch_sha(client, settings, installation_token)
    submission_id = secrets.token_hex(4)
    slug = _slug_from_path(path)
    branch = f"portal/update/{datetime.now(UTC).year}/{submission_id}-{slug}"

    create_branch(client, settings, installation_token, branch, base_sha)

    update_file_content(
        client,
        settings,
        installation_token,
        path,
        new_content,
        message=f"Atualiza {path} via ifrn-editorial-portal",
        branch=branch,
        sha=current["sha"],
    )

    pull_request = create_pull_request(
        client,
        settings,
        installation_token,
        title=f"Atualização: {slug}",
        head=branch,
        base=settings.github_base_branch,
        body=_build_pull_request_body(summary=request.summary, author=session["login"], path=path),
    )

    return SubmissionResponse(
        submission_id=submission_id,
        branch=branch,
        pull_request=PullRequestInfo(
            number=pull_request["number"],
            html_url=pull_request["html_url"],
            state=pull_request["state"],
        ),
    )
