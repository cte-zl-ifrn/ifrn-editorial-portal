import base64

import respx
from conftest import set_session_cookie
from httpx import Response

GITHUB_API = "https://api.github.com"
SAMPLE_PATH = "_docs/ambiente-virtual/acesso-moodle.md"


def _mock_installation_token(router: respx.MockRouter) -> None:
    router.post(f"{GITHUB_API}/app/installations/999/access_tokens").mock(
        return_value=Response(201, json={"token": "test-installation-token"})
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
def test_sample_document_returns_decoded_content_for_authorized_user(client, settings):
    set_session_cookie(client, settings, authorized=True, permission="write")
    _mock_installation_token(respx)

    raw_content = "---\ntitle: Acesso ao Moodle\n---\n\n# Como acessar o Moodle\n"
    encoded_content = base64.b64encode(raw_content.encode("utf-8")).decode("ascii")
    respx.get(
        f"{GITHUB_API}/repos/cte-zl-ifrn/central-ajuda/contents/{SAMPLE_PATH}"
    ).mock(
        return_value=Response(
            200,
            json={
                "type": "file",
                "encoding": "base64",
                "content": encoded_content,
                "path": SAMPLE_PATH,
                "name": "acesso-moodle.md",
                "sha": "8d233eaa7ad166d412ada7a87a8a28ab67072197",
            },
        )
    )

    response = client.get("/api/documents/sample")

    assert response.status_code == 200
    body = response.json()
    assert body["path"] == SAMPLE_PATH
    assert body["name"] == "acesso-moodle.md"
    assert body["content"] == raw_content
    assert body["sha"] == "8d233eaa7ad166d412ada7a87a8a28ab67072197"
    assert body["encoding"] == "utf-8"


@respx.mock
def test_sample_document_not_found_returns_404(client, settings):
    set_session_cookie(client, settings, authorized=True, permission="write")
    _mock_installation_token(respx)
    respx.get(
        f"{GITHUB_API}/repos/cte-zl-ifrn/central-ajuda/contents/{SAMPLE_PATH}"
    ).mock(return_value=Response(404, json={"message": "Not Found"}))

    response = client.get("/api/documents/sample")

    assert response.status_code == 404
    assert response.json()["error"] == "document_not_found"


@respx.mock
def test_sample_document_invalid_encoding_returns_502(client, settings):
    set_session_cookie(client, settings, authorized=True, permission="write")
    _mock_installation_token(respx)
    respx.get(
        f"{GITHUB_API}/repos/cte-zl-ifrn/central-ajuda/contents/{SAMPLE_PATH}"
    ).mock(
        return_value=Response(
            200,
            json={"type": "dir", "encoding": None, "path": SAMPLE_PATH, "name": "x", "sha": "x"},
        )
    )

    response = client.get("/api/documents/sample")

    assert response.status_code == 502
    assert response.json()["error"] == "invalid_document_encoding"


def test_sample_document_ignores_extra_query_params_trying_to_override_repository(client, settings):
    """RF-21: owner/repo/branch são fixos; parâmetros extras não têm efeito
    porque o endpoint não os declara nem os utiliza."""
    set_session_cookie(client, settings, authorized=False, permission="read")

    with respx.mock:
        response = client.get(
            "/api/documents/sample",
            params={"owner": "outra-org", "repo": "outro-repo", "branch": "outra-branch"},
        )

    assert response.status_code == 403
