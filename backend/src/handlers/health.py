from fastapi import APIRouter

from ..models import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Não exige autenticação nem acessa o GitHub — RF-28."""
    return HealthResponse(status="ok")
