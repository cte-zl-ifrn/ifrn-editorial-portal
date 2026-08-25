from fastapi import APIRouter

from ..dependencies import AuthorizedSessionDep, HttpClientDep, SettingsDep
from ..models import DocumentResponse
from ..services.document_service import read_sample_document

router = APIRouter(tags=["documents"])


@router.get("/api/documents/sample", response_model=DocumentResponse)
def get_sample_document(
    session: AuthorizedSessionDep,
    settings: SettingsDep,
    client: HttpClientDep,
) -> DocumentResponse:
    """Lê o documento de demonstração fixo — RF-17 a RF-21.

    `AuthorizedSessionDep` já garante sessão válida e usuário autorizado
    (RF-18) antes de qualquer chamada ao GitHub.
    """
    del session  # apenas para exigir autorização; não é usado no corpo
    return read_sample_document(client, settings)
