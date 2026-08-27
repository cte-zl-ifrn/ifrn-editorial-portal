from fastapi import APIRouter

from ..dependencies import AuthorizedSessionDep, HttpClientDep, SettingsDep
from ..logging import log_metric
from ..models import SubmissionRequest, SubmissionResponse
from ..services.submission_service import submit_document

router = APIRouter(tags=["submissions"])


@router.post("/api/submissions", response_model=SubmissionResponse, status_code=201)
def create_submission(
    request: SubmissionRequest,
    session: AuthorizedSessionDep,
    settings: SettingsDep,
    client: HttpClientDep,
) -> SubmissionResponse:
    """Cria uma branch, grava o documento e abre um Pull Request (Fase 3.1).

    `AuthorizedSessionDep` garante sessão válida e usuário autorizado
    antes de qualquer chamada de escrita ao GitHub.
    """
    response = submit_document(client, settings, request, session)
    log_metric("SubmissionCompleted")
    return response
