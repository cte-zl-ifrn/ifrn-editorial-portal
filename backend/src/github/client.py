"""Chamadas à API do GitHub usadas nas Fases 1, 2 e 3.

Duas identidades distintas usam este cliente (ver
docs/architecture/authentication-flow.md):
- o token de acesso OAuth do usuário, apenas para identificá-lo;
- o installation access token da GitHub App, para verificar permissão,
  ler e (desde a Fase 3) gravar conteúdo no repositório fixo.

A gravação (Fase 3, ver ADR-0011) usa chamadas sequenciais à Contents API
e à API de referências Git — não a Git Data API de blobs/trees.
"""

from __future__ import annotations

import base64
import binascii

import httpx

from ..config import Settings
from ..errors import DocumentNotFoundError, GithubCommunicationError, InvalidDocumentEncodingError

_ACCEPT_JSON = "application/vnd.github+json"


def exchange_code_for_token(client: httpx.Client, settings: Settings, code: str) -> str:
    response = client.post(
        f"{settings.github_oauth_base_url}/login/oauth/access_token",
        headers={"Accept": "application/json"},
        data={
            "client_id": settings.github_oauth_client_id,
            "client_secret": settings.github_oauth_client_secret,
            "code": code,
            "redirect_uri": settings.github_oauth_redirect_uri,
        },
    )
    if response.status_code != 200:
        raise GithubCommunicationError("Falha ao trocar o código OAuth por um token de acesso.")
    payload = response.json()
    token = payload.get("access_token")
    if not token:
        raise GithubCommunicationError("O GitHub não retornou um token de acesso válido.")
    return str(token)


def get_authenticated_user(client: httpx.Client, settings: Settings, user_token: str) -> dict:
    response = client.get(
        f"{settings.github_api_base_url}/user",
        headers={"Authorization": f"Bearer {user_token}", "Accept": _ACCEPT_JSON},
    )
    if response.status_code != 200:
        raise GithubCommunicationError("Falha ao identificar o usuário autenticado no GitHub.")
    return response.json()


def get_user_repository_permission(
    client: httpx.Client, settings: Settings, installation_token: str, username: str
) -> str:
    url = (
        f"{settings.github_api_base_url}/repos/"
        f"{settings.github_owner}/{settings.github_repository}/collaborators/{username}/permission"
    )
    response = client.get(
        url,
        headers={"Authorization": f"Bearer {installation_token}", "Accept": _ACCEPT_JSON},
    )
    if response.status_code == 404:
        return "none"
    if response.status_code != 200:
        raise GithubCommunicationError(
            "Falha ao verificar a permissão do usuário no repositório."
        )
    return str(response.json().get("permission", "none"))


def get_repository_content(
    client: httpx.Client, settings: Settings, installation_token: str, path: str
) -> dict:
    url = (
        f"{settings.github_api_base_url}/repos/"
        f"{settings.github_owner}/{settings.github_repository}/contents/{path}"
    )
    response = client.get(
        url,
        headers={"Authorization": f"Bearer {installation_token}", "Accept": _ACCEPT_JSON},
        params={"ref": settings.github_base_branch},
    )
    if response.status_code == 404:
        raise DocumentNotFoundError(f"Documento '{path}' não encontrado no repositório.")
    if response.status_code != 200:
        raise GithubCommunicationError("Falha ao ler o conteúdo do repositório.")

    payload = response.json()
    if payload.get("type") != "file" or payload.get("encoding") != "base64":
        raise InvalidDocumentEncodingError(
            "O conteúdo retornado pelo GitHub não é um arquivo em base64."
        )
    try:
        decoded = base64.b64decode(payload["content"]).decode("utf-8")
    except (binascii.Error, UnicodeDecodeError) as exc:
        raise InvalidDocumentEncodingError(
            "Não foi possível decodificar o conteúdo do documento como UTF-8."
        ) from exc

    return {
        "path": payload["path"],
        "name": payload["name"],
        "content": decoded,
        "sha": payload["sha"],
    }


def get_main_branch_sha(client: httpx.Client, settings: Settings, installation_token: str) -> str:
    url = (
        f"{settings.github_api_base_url}/repos/"
        f"{settings.github_owner}/{settings.github_repository}/git/ref/heads/"
        f"{settings.github_base_branch}"
    )
    response = client.get(
        url, headers={"Authorization": f"Bearer {installation_token}", "Accept": _ACCEPT_JSON}
    )
    if response.status_code != 200:
        raise GithubCommunicationError("Falha ao obter o SHA atual da branch base.")
    return str(response.json()["object"]["sha"])


def create_branch(
    client: httpx.Client,
    settings: Settings,
    installation_token: str,
    branch_name: str,
    base_sha: str,
) -> None:
    url = (
        f"{settings.github_api_base_url}/repos/"
        f"{settings.github_owner}/{settings.github_repository}/git/refs"
    )
    response = client.post(
        url,
        headers={"Authorization": f"Bearer {installation_token}", "Accept": _ACCEPT_JSON},
        json={"ref": f"refs/heads/{branch_name}", "sha": base_sha},
    )
    if response.status_code != 201:
        raise GithubCommunicationError("Falha ao criar a branch da submissão.")


def update_file_content(
    client: httpx.Client,
    settings: Settings,
    installation_token: str,
    path: str,
    content: str | bytes,
    message: str,
    branch: str,
    sha: str | None = None,
) -> dict:
    """`sha` é obrigatório para atualizar um arquivo existente (Fase 3.1) e
    deve ser omitido para criar um arquivo novo (assets, Fase 3.2) — a
    Contents API rejeita a chamada se os dois casos forem invertidos."""
    url = (
        f"{settings.github_api_base_url}/repos/"
        f"{settings.github_owner}/{settings.github_repository}/contents/{path}"
    )
    raw_content = content.encode("utf-8") if isinstance(content, str) else content
    encoded_content = base64.b64encode(raw_content).decode("ascii")
    payload = {"message": message, "content": encoded_content, "branch": branch}
    if sha is not None:
        payload["sha"] = sha
    response = client.put(
        url,
        headers={"Authorization": f"Bearer {installation_token}", "Accept": _ACCEPT_JSON},
        json=payload,
    )
    if response.status_code not in (200, 201):
        raise GithubCommunicationError("Falha ao gravar o arquivo na branch da submissão.")
    return response.json()


def create_pull_request(
    client: httpx.Client,
    settings: Settings,
    installation_token: str,
    title: str,
    head: str,
    base: str,
    body: str,
) -> dict:
    url = (
        f"{settings.github_api_base_url}/repos/"
        f"{settings.github_owner}/{settings.github_repository}/pulls"
    )
    response = client.post(
        url,
        headers={"Authorization": f"Bearer {installation_token}", "Accept": _ACCEPT_JSON},
        json={"title": title, "head": head, "base": base, "body": body},
    )
    if response.status_code != 201:
        raise GithubCommunicationError("Falha ao criar o Pull Request.")
    return response.json()
