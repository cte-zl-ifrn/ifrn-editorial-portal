import base64

import respx
from conftest import set_session_cookie
from httpx import Response

GITHUB_API = "https://api.github.com"
REPO = "cte-zl-ifrn/central-ajuda"
SAMPLE_PATH = "_docs/proitec/como-fazer-cursos.md"
CURRENT_SHA = "8d233eaa7ad166d412ada7a87a8a28ab67072197"
RAW_CONTENT = (
    "---\ntitle: Como fazer os cursos do ProITEC?\n---\n"
    "\n# Como fazer os cursos do ProITEC?\n\nTexto de introdução.\n"
)


def _mock_installation_token(router: respx.MockRouter) -> None:
    router.post(f"{GITHUB_API}/app/installations/999/access_tokens").mock(
        return_value=Response(201, json={"token": "test-installation-token"})
    )


def _mock_current_content(router: respx.MockRouter, sha: str = CURRENT_SHA) -> respx.Route:
    encoded = base64.b64encode(RAW_CONTENT.encode("utf-8")).decode("ascii")
    return router.get(f"{GITHUB_API}/repos/{REPO}/contents/{SAMPLE_PATH}").mock(
        return_value=Response(
            200,
            json={
                "type": "file",
                "encoding": "base64",
                "content": encoded,
                "path": SAMPLE_PATH,
                "name": "como-fazer-cursos.md",
                "sha": sha,
            },
        )
    )


def _mock_main_branch_sha(router: respx.MockRouter, sha: str = "main-sha-123") -> respx.Route:
    return router.get(f"{GITHUB_API}/repos/{REPO}/git/ref/heads/main").mock(
        return_value=Response(200, json={"object": {"sha": sha}})
    )


def _mock_create_branch(router: respx.MockRouter, *, status_code: int = 201) -> respx.Route:
    return router.post(f"{GITHUB_API}/repos/{REPO}/git/refs").mock(
        return_value=Response(status_code, json={"ref": "refs/heads/x"})
    )


def _mock_update_file(router: respx.MockRouter, *, status_code: int = 200) -> respx.Route:
    return router.put(f"{GITHUB_API}/repos/{REPO}/contents/{SAMPLE_PATH}").mock(
        return_value=Response(status_code, json={"content": {"sha": "new-sha"}})
    )


def _mock_create_pull_request(
    router: respx.MockRouter, *, status_code: int = 201, number: int = 42
) -> respx.Route:
    return router.post(f"{GITHUB_API}/repos/{REPO}/pulls").mock(
        return_value=Response(
            status_code,
            json={
                "number": number,
                "html_url": f"https://github.com/{REPO}/pull/{number}",
                "state": "open",
            },
        )
    )


def _payload(**overrides: object) -> dict:
    payload = {
        "body": "\n# Novo corpo\n\nEditado.\n",
        "base_sha": CURRENT_SHA,
        "summary": "Atualiza o texto de introdução.",
    }
    payload.update(overrides)
    return payload


def test_submission_requires_authentication(client):
    response = client.post("/api/submissions", json=_payload())

    assert response.status_code == 401
    assert response.json()["error"] == "unauthenticated"


def test_submission_rejects_unauthorized_user(client, settings):
    set_session_cookie(client, settings, authorized=False, permission="read")

    with respx.mock:
        response = client.post("/api/submissions", json=_payload())

    assert response.status_code == 403
    assert response.json()["error"] == "unauthorized"


def test_submission_rejects_empty_body(client, settings):
    set_session_cookie(client, settings, authorized=True, permission="write")

    with respx.mock:
        response = client.post("/api/submissions", json=_payload(body=""))

    assert response.status_code == 422
    assert response.json()["error"] == "invalid_request"


def test_submission_rejects_empty_summary(client, settings):
    set_session_cookie(client, settings, authorized=True, permission="write")

    with respx.mock:
        response = client.post("/api/submissions", json=_payload(summary=""))

    assert response.status_code == 422
    assert response.json()["error"] == "invalid_request"


@respx.mock
def test_submission_success_creates_branch_commit_and_pull_request(client, settings):
    set_session_cookie(client, settings, authorized=True, permission="write")
    _mock_installation_token(respx)
    _mock_current_content(respx)
    _mock_main_branch_sha(respx)
    _mock_create_branch(respx)
    _mock_update_file(respx)
    _mock_create_pull_request(respx)

    response = client.post("/api/submissions", json=_payload())

    assert response.status_code == 201
    body = response.json()
    assert body["branch"].startswith("portal/update/")
    assert body["branch"].endswith("-como-fazer-cursos")
    assert body["pull_request"] == {
        "number": 42,
        "html_url": f"https://github.com/{REPO}/pull/42",
        "state": "open",
    }
    assert "submission_id" in body


@respx.mock
def test_submission_conflict_when_base_sha_is_stale(client, settings):
    set_session_cookie(client, settings, authorized=True, permission="write")
    _mock_installation_token(respx)
    _mock_current_content(respx, sha="a-different-sha-now")
    branch_route = _mock_create_branch(respx)
    file_route = _mock_update_file(respx)
    pr_route = _mock_create_pull_request(respx)

    response = client.post("/api/submissions", json=_payload(base_sha=CURRENT_SHA))

    assert response.status_code == 409
    assert response.json()["error"] == "document_conflict"
    # Nada deve ser gravado quando há conflito.
    assert branch_route.call_count == 0
    assert file_route.call_count == 0
    assert pr_route.call_count == 0


@respx.mock
def test_submission_fails_when_branch_creation_fails(client, settings):
    set_session_cookie(client, settings, authorized=True, permission="write")
    _mock_installation_token(respx)
    _mock_current_content(respx)
    _mock_main_branch_sha(respx)
    _mock_create_branch(respx, status_code=422)
    file_route = _mock_update_file(respx)
    pr_route = _mock_create_pull_request(respx)

    response = client.post("/api/submissions", json=_payload())

    assert response.status_code == 502
    assert response.json()["error"] == "github_communication_error"
    assert file_route.call_count == 0
    assert pr_route.call_count == 0


@respx.mock
def test_submission_fails_when_commit_fails(client, settings):
    set_session_cookie(client, settings, authorized=True, permission="write")
    _mock_installation_token(respx)
    _mock_current_content(respx)
    _mock_main_branch_sha(respx)
    _mock_create_branch(respx)
    _mock_update_file(respx, status_code=409)
    pr_route = _mock_create_pull_request(respx)

    response = client.post("/api/submissions", json=_payload())

    assert response.status_code == 502
    assert response.json()["error"] == "github_communication_error"
    assert pr_route.call_count == 0


@respx.mock
def test_submission_fails_when_pull_request_creation_fails(client, settings):
    set_session_cookie(client, settings, authorized=True, permission="write")
    _mock_installation_token(respx)
    _mock_current_content(respx)
    _mock_main_branch_sha(respx)
    _mock_create_branch(respx)
    _mock_update_file(respx)
    _mock_create_pull_request(respx, status_code=422)

    response = client.post("/api/submissions", json=_payload())

    assert response.status_code == 502
    assert response.json()["error"] == "github_communication_error"


@respx.mock
def test_submission_ignores_client_supplied_repository_overrides(client, settings):
    """RF-21: owner/repo/branch são fixos; parâmetros extras no corpo não
    têm efeito porque o modelo de requisição não os declara."""
    set_session_cookie(client, settings, authorized=True, permission="write")
    _mock_installation_token(respx)
    _mock_current_content(respx)
    _mock_main_branch_sha(respx)
    _mock_create_branch(respx)
    _mock_update_file(respx)
    _mock_create_pull_request(respx)

    response = client.post(
        "/api/submissions",
        json=_payload(owner="outra-org", repo="outro-repo", branch="outra-branch"),
    )

    assert response.status_code == 201
