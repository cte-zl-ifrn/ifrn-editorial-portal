"""Configuração do backend, carregada de variáveis de ambiente.

owner/repo/branch são constantes do projeto (ver ADR-0001 e ADR-0004) e
nunca devem ser aceitos como entrada de requisição — ver
docs/requirements/functional-requirements.md (RF-21).
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Repositório de conteúdo — fixo, não configurável por requisição.
    github_owner: str = "cte-zl-ifrn"
    github_repository: str = "central-ajuda"
    github_base_branch: str = "main"
    sample_document_path: str = "_docs/ambiente-virtual/acesso-moodle.md"

    # OAuth do GitHub (identidade da pessoa usuária).
    github_oauth_client_id: str = ""
    github_oauth_client_secret: str = ""
    github_oauth_redirect_uri: str = "http://localhost:8000/auth/callback"

    # GitHub App (leitura de conteúdo).
    github_app_id: str = ""
    github_app_private_key: str = ""
    github_app_installation_id: str | None = None

    # Sessão e estado OAuth.
    session_secret: str = Field(default="dev-only-insecure-secret")
    session_cookie_name: str = "portal_session"
    session_max_age_seconds: int = 1800
    oauth_state_cookie_name: str = "portal_oauth_state"
    oauth_state_max_age_seconds: int = 300

    # Frontend / CORS.
    frontend_url: str = "http://localhost:5173"
    cookie_secure: bool = False
    cookie_samesite: str = "lax"

    # GitHub API.
    github_api_base_url: str = "https://api.github.com"
    github_oauth_base_url: str = "https://github.com"


@lru_cache
def get_settings() -> Settings:
    return Settings()
