"""Configuração do backend, carregada de variáveis de ambiente.

owner/repo/branch são constantes do projeto (ver ADR-0001 e ADR-0004) e
nunca devem ser aceitos como entrada de requisição — ver
docs/requirements/functional-requirements.md (RF-21).
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Repositório de conteúdo — fixo, não configurável por requisição.
    github_owner: str = "cte-zl-ifrn"
    github_repository: str = "central-ajuda"
    github_base_branch: str = "main"
    # Trocado na Fase 2.1 (era _docs/ambiente-virtual/acesso-moodle.md):
    # este documento exercita listas com marcadores, o que o anterior não
    # tinha — ver docs/phase-2.1-plan.md.
    sample_document_path: str = "_docs/proitec/como-fazer-cursos.md"

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

    @field_validator("github_app_private_key")
    @classmethod
    def _normalize_private_key(cls, value: str) -> str:
        """Aceita a chave colada em uma única linha com `\\n` literais
        (comum ao copiar de um .pem para uma variável de ambiente) além do
        PEM multilinha padrão. Sem isso, o PyJWT falha ao interpretar o PEM
        porque os `\\n` nunca viram quebras de linha reais."""
        if not value:
            return value
        normalized = value.strip()
        if normalized[0] in "'\"" and normalized[-1] == normalized[0]:
            normalized = normalized[1:-1]
        if "\\n" in normalized and "\n" not in normalized:
            normalized = normalized.replace("\\n", "\n")
        return normalized.strip() + "\n"


@lru_cache
def get_settings() -> Settings:
    return Settings()
