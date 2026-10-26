import base64

import respx
from conftest import set_session_cookie
from httpx import Response

GITHUB_API = "https://api.github.com"
SAMPLE_PATH = "_docs/proitec/como-fazer-cursos.md"


def _mock_installation_token(router: respx.MockRouter) -> None:
    router.post(f"{GITHUB_API}/app/installations/999/access_tokens").mock(
        return_value=Response(201, json={"token": "test-installation-token"})
    )


def _mock_content(router: respx.MockRouter, raw_content: str, *, path: str = SAMPLE_PATH) -> None:
    encoded_content = base64.b64encode(raw_content.encode("utf-8")).decode("ascii")
    router.get(f"{GITHUB_API}/repos/cte-zl-ifrn/central-ajuda/contents/{path}").mock(
        return_value=Response(
            200,
            json={
                "type": "file",
                "encoding": "base64",
                "content": encoded_content,
                "path": path,
                "name": path.rsplit("/", 1)[-1],
                "sha": "8d233eaa7ad166d412ada7a87a8a28ab67072197",
            },
        )
    )


def test_sample_document_requires_authentication(client):
    response = client.get("/api/documents/sample")

    assert response.status_code == 401
    assert response.json()["error"] == "unauthenticated"


def test_sample_document_rejects_unauthorized_user(client, settings):
    set_session_cookie(client, settings, authorized=False, permission="read")

    with respx.mock:
        response = client.get("/api/documents/sample")

    assert response.status_code == 403
    assert response.json()["error"] == "unauthorized"


@respx.mock
def test_sample_document_returns_split_front_matter_and_body(client, settings):
    set_session_cookie(client, settings, authorized=True, permission="write")
    _mock_installation_token(respx)

    raw_content = (
        "---\ntitle: Como fazer os cursos do ProITEC?\ncategories:\n  - proitec\n---\n"
        "\n# Como fazer os cursos do ProITEC?\n\nTexto de introdução.\n"
    )
    _mock_content(respx, raw_content)

    response = client.get("/api/documents/sample")

    assert response.status_code == 200
    body = response.json()
    assert body["path"] == SAMPLE_PATH
    assert body["name"] == "como-fazer-cursos.md"
    assert body["sha"] == "8d233eaa7ad166d412ada7a87a8a28ab67072197"
    assert body["front_matter"] == {
        "title": "Como fazer os cursos do ProITEC?",
        "categories": ["proitec"],
    }
    assert body["front_matter_raw"] == (
        "---\ntitle: Como fazer os cursos do ProITEC?\ncategories:\n  - proitec\n---\n"
    )
    assert body["body"] == "\n# Como fazer os cursos do ProITEC?\n\nTexto de introdução.\n"
    # Invariante da ADR-0009: front_matter_raw + body reproduz o original.
    assert body["front_matter_raw"] + body["body"] == raw_content


@respx.mock
def test_sample_document_without_front_matter_returns_empty_front_matter(client, settings):
    set_session_cookie(client, settings, authorized=True, permission="write")
    _mock_installation_token(respx)

    raw_content = "# Documento sem front matter\n\nConteúdo.\n"
    _mock_content(respx, raw_content)

    response = client.get("/api/documents/sample")

    assert response.status_code == 200
    body = response.json()
    assert body["front_matter"] == {}
    assert body["front_matter_raw"] == ""
    assert body["body"] == raw_content


@respx.mock
def test_sample_document_with_malformed_front_matter_returns_502(client, settings):
    set_session_cookie(client, settings, authorized=True, permission="write")
    _mock_installation_token(respx)

    raw_content = "---\ntitle: [unterminated\n---\n\n# Corpo\n"
    _mock_content(respx, raw_content)

    response = client.get("/api/documents/sample")

    assert response.status_code == 502
    assert response.json()["error"] == "invalid_front_matter"


@respx.mock
def test_sample_document_not_found_returns_404(client, settings):
    set_session_cookie(client, settings, authorized=True, permission="write")
    _mock_installation_token(respx)
    respx.get(f"{GITHUB_API}/repos/cte-zl-ifrn/central-ajuda/contents/{SAMPLE_PATH}").mock(
        return_value=Response(404, json={"message": "Not Found"})
    )

    response = client.get("/api/documents/sample")

    assert response.status_code == 404
    assert response.json()["error"] == "document_not_found"


@respx.mock
def test_sample_document_invalid_encoding_returns_502(client, settings):
    set_session_cookie(client, settings, authorized=True, permission="write")
    _mock_installation_token(respx)
    respx.get(f"{GITHUB_API}/repos/cte-zl-ifrn/central-ajuda/contents/{SAMPLE_PATH}").mock(
        return_value=Response(
            200,
            json={"type": "dir", "encoding": None, "path": SAMPLE_PATH, "name": "x", "sha": "x"},
        )
    )

    response = client.get("/api/documents/sample")

    assert response.status_code == 502
    assert response.json()["error"] == "invalid_document_encoding"


def test_sample_document_ignores_extra_query_params_trying_to_override_repository(
    client, settings
):
    """RF-21: owner/repo/branch são fixos; parâmetros extras não têm efeito
    porque o endpoint não os declara nem os utiliza."""
    set_session_cookie(client, settings, authorized=False, permission="read")

    with respx.mock:
        response = client.get(
            "/api/documents/sample",
            params={"owner": "outra-org", "repo": "outro-repo", "branch": "outra-branch"},
        )

    assert response.status_code == 403
