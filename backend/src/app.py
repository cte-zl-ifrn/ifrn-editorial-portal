"""Aplicação FastAPI — ver docs/api/openapi.yaml para o contrato completo."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import get_settings
from .errors import PortalError
from .handlers import auth, documents, health, me
from .logging import (
    configure_logging,
    get_logger,
    log_event,
    new_correlation_id,
    set_correlation_id,
)

configure_logging()
logger = get_logger(__name__)


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="IFRN Editorial Portal API — Fase 1",
        version="0.1.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.frontend_url],
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def correlation_id_middleware(request: Request, call_next):
        correlation_id = request.headers.get("x-correlation-id", new_correlation_id())
        set_correlation_id(correlation_id)
        log_event(logger, "request.received", path=request.url.path, method=request.method)
        response = await call_next(request)
        response.headers["X-Correlation-Id"] = correlation_id
        return response

    @app.exception_handler(PortalError)
    async def portal_error_handler(request: Request, exc: PortalError) -> JSONResponse:
        from .logging import get_correlation_id

        log_event(
            logger,
            "request.error",
            path=request.url.path,
            error=exc.error_code,
            status_code=exc.status_code,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.error_code,
                "message": exc.message,
                "correlation_id": get_correlation_id(),
            },
        )

    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(me.router)
    app.include_router(documents.router)

    return app


app = create_app()
