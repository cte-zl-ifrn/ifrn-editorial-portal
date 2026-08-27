"""Aplicação FastAPI — ver docs/api/openapi.yaml para o contrato completo."""

from __future__ import annotations

import time

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import get_settings
from .errors import PortalError
from .handlers import auth, documents, health, me, submissions
from .logging import (
    configure_logging,
    get_logger,
    log_event,
    log_metric,
    new_correlation_id,
    set_correlation_id,
)

configure_logging()
logger = get_logger(__name__)


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="IFRN Editorial Portal API — Fase 1 / Fase 2 / Fase 3.1",
        version="0.3.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.frontend_url],
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def request_size_limit_middleware(request: Request, call_next):
        """Teto sobre o corpo inteiro de uma submissão (Fase 4.3,
        ADR-0013) — não substitui os limites por asset já existentes
        (`assets/validation.py`), é uma proteção adicional contra um
        payload anormalmente grande, verificada antes de qualquer
        parsing. Registrado antes de `access_log_middleware` (mais
        interno) para que uma rejeição aqui ainda apareça no log de
        acesso, como qualquer outra resposta."""
        if request.method == "POST" and request.url.path == "/api/submissions":
            content_length = request.headers.get("content-length")
            if content_length is not None:
                try:
                    body_size = int(content_length)
                except ValueError:
                    body_size = None
                if body_size is not None and body_size > get_settings().max_submission_body_bytes:
                    from .logging import get_correlation_id

                    return JSONResponse(
                        status_code=413,
                        content={
                            "error": "payload_too_large",
                            "message": "O corpo da requisição excede o tamanho máximo permitido.",
                            "correlation_id": get_correlation_id(),
                        },
                    )
        return await call_next(request)

    @app.middleware("http")
    async def access_log_middleware(request: Request, call_next):
        """Registro de acesso por requisição (Fase 4.2) — uma linha
        estruturada ao final de toda requisição, mesmo em caso de exceção
        não tratada (por isso o `try/finally`: sem ele, um bug genuíno no
        handler faria a requisição nunca aparecer no log de acesso)."""
        correlation_id = request.headers.get("x-correlation-id", new_correlation_id())
        set_correlation_id(correlation_id)
        started_at = time.perf_counter()
        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
            response.headers["X-Correlation-Id"] = correlation_id
            return response
        finally:
            duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
            log_event(
                logger,
                "request.completed",
                method=request.method,
                path=request.url.path,
                status_code=status_code,
                duration_ms=duration_ms,
            )
            log_metric("RequestCount", dimensions={"Route": request.url.path})
            if status_code >= 400:
                log_metric(
                    "ErrorCount",
                    dimensions={"Route": request.url.path, "StatusCode": str(status_code)},
                )

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

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        from .logging import get_correlation_id

        log_event(logger, "request.error", path=request.url.path, error="invalid_request")
        return JSONResponse(
            status_code=422,
            content={
                "error": "invalid_request",
                "message": "Requisição inválida.",
                "correlation_id": get_correlation_id(),
            },
        )

    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(me.router)
    app.include_router(documents.router)
    app.include_router(submissions.router)

    return app


app = create_app()
