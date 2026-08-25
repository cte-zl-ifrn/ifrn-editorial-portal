"""Erros de domínio do backend, mapeados para respostas HTTP nos handlers.

Mensagens não devem conter tokens, chaves ou detalhes internos — ver
docs/requirements/functional-requirements.md (RF-22 a RF-25).
"""

from __future__ import annotations


class PortalError(Exception):
    """Erro base do domínio do portal."""

    error_code = "internal_error"
    status_code = 500

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or self.error_code)
        self.message = message or "Erro interno."


class InvalidOAuthStateError(PortalError):
    error_code = "invalid_oauth_state"
    status_code = 400


class GithubCommunicationError(PortalError):
    error_code = "github_communication_error"
    status_code = 502


class NotAuthenticatedError(PortalError):
    error_code = "unauthenticated"
    status_code = 401


class NotAuthorizedError(PortalError):
    error_code = "unauthorized"
    status_code = 403


class DocumentNotFoundError(PortalError):
    error_code = "document_not_found"
    status_code = 404


class InvalidDocumentEncodingError(PortalError):
    error_code = "invalid_document_encoding"
    status_code = 502


class InvalidFrontMatterError(PortalError):
    error_code = "invalid_front_matter"
    status_code = 502


class MissingConfigurationError(PortalError):
    error_code = "missing_configuration"
    status_code = 500
