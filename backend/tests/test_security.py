from unittest.mock import patch

from conftest import set_session_cookie
from fastapi.testclient import TestClient

from src.app import app


def test_every_response_includes_the_security_headers(client):
    response = client.get("/health")

    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "no-referrer"
    assert response.headers["Content-Security-Policy"] == "default-src 'none'"


def test_docs_paths_are_exempt_from_the_content_security_policy(client):
    """A UI do FastAPI (`/docs`) carrega script/estilo de um CDN externo
    — quebraria com `default-src 'none'`. Os demais cabeçalhos continuam
    aplicados normalmente."""
    response = client.get("/docs")

    assert "Content-Security-Policy" not in response.headers
    assert response.headers["X-Content-Type-Options"] == "nosniff"


def test_write_request_without_csrf_header_is_rejected_even_with_a_valid_session(
    client, settings
):
    set_session_cookie(client, settings, authorized=True, permission="write")
    del client.headers["X-Portal-Client"]

    response = client.post(
        "/api/submissions",
        json={"body": "x", "base_sha": "abc", "summary": "y"},
    )

    assert response.status_code == 403
    assert response.json()["error"] == "missing_csrf_header"


def test_write_request_with_csrf_header_is_not_blocked_by_the_csrf_check(client, settings):
    """O cabeçalho já é enviado por padrão pela fixture `client` — aqui
    confirma-se que, com ele presente, a requisição chega além do
    middleware de CSRF (rejeitada por outro motivo — autenticação —, não
    por `missing_csrf_header`)."""
    response = client.post(
        "/api/submissions", json={"body": "x", "base_sha": "abc", "summary": "y"}
    )

    assert response.status_code == 401
    assert response.json()["error"] == "unauthenticated"


def test_read_request_without_csrf_header_is_not_blocked(client):
    """A exigência do cabeçalho é só para métodos que alteram estado — a
    Fase 4.4 (ADR-0014) não afeta GET."""
    del client.headers["X-Portal-Client"]

    response = client.get("/health")

    assert response.status_code == 200


def test_unexpected_exception_never_leaks_internal_detail():
    """Um bug genuíno (não um erro de domínio conhecido) ainda deve
    produzir o mesmo envelope {error, message, correlation_id} de toda
    outra resposta de erro — nunca um traceback ou texto interno.

    Usa um TestClient próprio, com `raise_server_exceptions=False`: o
    comportamento padrão do TestClient é relançar qualquer exceção que
    tenha atravessado a aplicação, mesmo quando um exception handler já a
    tratou e devolveu uma resposta normal — útil para depuração, mas não
    é isso que se quer verificar aqui (a resposta HTTP real ao cliente).
    """
    no_raise_client = TestClient(app, raise_server_exceptions=False)
    no_raise_client.headers["X-Portal-Client"] = "1"

    with patch("src.handlers.health.HealthResponse", side_effect=RuntimeError("boom, segredo=xyz")):
        response = no_raise_client.get("/health")

    assert response.status_code == 500
    body = response.json()
    assert body["error"] == "internal_error"
    assert "boom" not in body["message"]
    assert "segredo" not in str(body)
    assert set(body.keys()) == {"error", "message", "correlation_id"}
