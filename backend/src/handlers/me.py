from fastapi import APIRouter

from ..dependencies import CurrentSessionDep
from ..models import GithubUser, MeResponse

router = APIRouter(tags=["me"])


@router.get("/api/me", response_model=MeResponse)
def me(session: CurrentSessionDep) -> MeResponse:
    """Retorna identidade e status de autorização — RF-11, RF-12."""
    return MeResponse(
        user=GithubUser(
            login=session["login"],
            name=session.get("name"),
            avatar_url=session.get("avatar_url"),
        ),
        authorized=session["authorized"],
        repository_permission=session.get("repository_permission"),
    )
