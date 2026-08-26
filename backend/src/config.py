"""Configuração do backend, carregada de variáveis de ambiente.

owner/repo/branch são constantes do projeto (ver ADR-0001 e ADR-0004) e
nunca devem ser aceitos como entrada de requisição — ver
docs/requirements/functional-requirements.md (RF-21).
"""

from __future__ import annotations

import json
import os
from functools import lru_cache

import boto3
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Nome da variável de ambiente com o ARN do segredo do Secrets Manager
# (ver ADR-0012). Só definida em produção (injetada pelo template SAM);
# ausente em desenvolvimento local, onde `.env` continua sendo a fonte.
SECRETS_MANAGER_SECRET_ARN_ENV_VAR = "SECRETS_MANAGER_SECRET_ARN"

# Chaves do segredo único no Secrets Manager, mapeadas para os campos
# correspondentes de `Settings` (ADR-0012).
_SECRETS_MANAGER_KEY_MAP = {
    "GITHUB_OAUTH_CLIENT_SECRET": "github_oauth_client_secret",
    "GITHUB_APP_ID": "github_app_id",
    "GITHUB_APP_PRIVATE_KEY": "github_app_private_key",
    "SESSION_SECRET": "session_secret",
}


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

    # Assets (Fase 3.2, ADR-0007) — limites de tamanho por tipo.
    max_image_size_bytes: int = 5_000_000
    max_file_size_bytes: int = 20_000_000

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


def _load_secrets_manager_overrides(secret_arn: str) -> dict[str, str]:
    """Busca o segredo único do Secrets Manager (ADR-0012) e retorna os
    valores a sobrescrever em `Settings`. Deliberadamente não captura
    exceções: uma falha aqui deve interromper a inicialização (nunca cair
    silenciosamente nos valores padrão inseguros de `Settings`)."""
    client = boto3.client("secretsmanager")
    response = client.get_secret_value(SecretId=secret_arn)
    secret = json.loads(response["SecretString"])
    return {
        field_name: secret[secret_key]
        for secret_key, field_name in _SECRETS_MANAGER_KEY_MAP.items()
    }


@lru_cache
def get_settings() -> Settings:
    secret_arn = os.environ.get(SECRETS_MANAGER_SECRET_ARN_ENV_VAR)
    overrides = _load_secrets_manager_overrides(secret_arn) if secret_arn else {}
    return Settings(**overrides)
