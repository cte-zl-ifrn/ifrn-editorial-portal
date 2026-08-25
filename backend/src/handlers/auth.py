from fastapi import APIRouter, Query, Request, Response
from fastapi.responses import RedirectResponse

from ..auth.session import create_session_cookie_value
from ..dependencies import HttpClientDep, SettingsDep
from ..logging import get_logger, log_event
from ..services.auth_service import build_authorize_url, complete_login

router = APIRouter(tags=["auth"])
logger = get_logger(__name__)


@router.get("/auth/login")
def login(settings: SettingsDep) -> RedirectResponse:
    """Inicia o fluxo OAuth — RF-01, RF-02."""
    authorize_url, state = build_authorize_url(settings)
    response = RedirectResponse(url=authorize_url, status_code=302)
    response.set_cookie(
        key=settings.oauth_state_cookie_name,
        value=state,
        max_age=settings.oauth_state_max_age_seconds,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,  # type: ignore[arg-type]
    )
    log_event(logger, "auth.login.started")
    return response


@router.get("/auth/callback")
def callback(
    request: Request,
    settings: SettingsDep,
    client: HttpClientDep,
    code: str = Query(...),
    state: str = Query(...),
) -> RedirectResponse:
    """Valida state, autentica o usuário e cria a sessão — RF-03 a RF-07."""
    state_cookie_value = request.cookies.get(settings.oauth_state_cookie_name)

    session_data = complete_login(
        client,
        settings,
        code=code,
        state=state,
        state_cookie_value=state_cookie_value,
    )

    cookie_value = create_session_cookie_value(settings, session_data)
    response = RedirectResponse(url=settings.frontend_url, status_code=302)
    response.delete_cookie(settings.oauth_state_cookie_name)
    response.set_cookie(
        key=settings.session_cookie_name,
        value=cookie_value,
        max_age=settings.session_max_age_seconds,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,  # type: ignore[arg-type]
    )
    log_event(
        logger,
        "auth.login.completed",
        login=session_data["login"],
        authorized=session_data["authorized"],
    )
    return response


@router.post("/auth/logout", status_code=204)
def logout(settings: SettingsDep) -> Response:
    """Idempotente — RF-26, RF-27."""
    response = Response(status_code=204)
    response.delete_cookie(settings.session_cookie_name)
    log_event(logger, "auth.logout")
    return response
