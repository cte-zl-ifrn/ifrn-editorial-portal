"""Escrita de um documento (e, desde a Fase 3.2, seus assets) no
central-ajuda: branch, commit(s) e Pull Request.

Ver ADR-0011: o backend relê o documento imediatamente antes de gravar e
compara com `base_sha` (conflito de edição concorrente); o front matter
sempre vem dessa releitura, nunca do que o cliente enviou; a gravação usa
chamadas sequenciais à Contents API, não a Git Data API. Ver ADR-0007 e
docs/phase-3.2-plan.md para assets: o diretório final é sempre calculado
aqui a partir do documento fixo, nunca aceito do cliente; assets são
validados integralmente antes de qualquer chamada ao GitHub, para que um
asset inválido nunca deixe branch/commit/PR pela metade.
"""

from __future__ import annotations

import secrets
from datetime import UTC, datetime

import httpx

from ..assets import ValidatedAsset, validate_asset
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

_ASSET_DIRECTORIES = {"image": "assets/images", "file": "assets/files"}


def _slug_from_path(path: str) -> str:
    name = path.rsplit("/", 1)[-1]
    return name.removesuffix(".md")


def _category_from_path(path: str) -> str:
    """Documentos seguem `_docs/{categoria}/{arquivo}.md` (seção 8.2 do
    documento de arquitetura) — a mesma categoria é usada para o
    diretório dos assets do documento (ADR-0007)."""
    return path.split("/")[1]


def _asset_path(settings: Settings, asset: ValidatedAsset) -> str:
    category = _category_from_path(settings.sample_document_path)
    directory = _ASSET_DIRECTORIES[asset.kind]
    return f"{directory}/{category}/{asset.filename}"


def _build_pull_request_body(*, summary: str, author: str, files: list[str]) -> str:
    now = datetime.now(UTC).isoformat()
    files_list = "\n".join(f"- `{file_path}`" for file_path in files)
    return (
        "## Alteração proposta\n\n"
        f"{summary}\n\n"
        "## Autor da solicitação\n\n"
        f"- Usuário: @{author}\n"
        f"- Data: {now}\n"
        "- Origem: ifrn-editorial-portal\n\n"
        "## Arquivos alterados\n\n"
        f"{files_list}\n\n"
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
    # Assets são validados antes de qualquer chamada ao GitHub — um asset
    # inválido nunca deve deixar uma branch ou commit pela metade.
    validated_assets = [
        validate_asset(
            settings,
            kind=asset.kind,
            filename=asset.filename,
            content_base64=asset.content,
            alt=asset.alt,
        )
        for asset in request.assets
    ]
    asset_paths = [_asset_path(settings, asset) for asset in validated_assets]

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

    for asset, asset_path in zip(validated_assets, asset_paths, strict=True):
        update_file_content(
            client,
            settings,
            installation_token,
            asset_path,
            asset.binary_content,
            message=f"Adiciona {asset_path} via ifrn-editorial-portal",
            branch=branch,
            sha=None,  # arquivo novo — nunca uma sobrescrita (ADR-0007).
        )

    pull_request = create_pull_request(
        client,
        settings,
        installation_token,
        title=f"Atualização: {slug}",
        head=branch,
        base=settings.github_base_branch,
        body=_build_pull_request_body(
            summary=request.summary, author=session["login"], files=[path, *asset_paths]
        ),
    )

    return SubmissionResponse(
        submission_id=submission_id,
        branch=branch,
        pull_request=PullRequestInfo(
            number=pull_request["number"],
            html_url=pull_request["html_url"],
            state=pull_request["state"],
        ),
        asset_paths=asset_paths,
    )
