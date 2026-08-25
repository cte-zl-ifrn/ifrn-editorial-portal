import respx
from httpx import Response

GITHUB_API = "https://api.github.com"
GITHUB_WEB = "https://github.com"


def _mock_successful_github(router: respx.MockRouter, permission: str = "write") -> None:
    router.post(f"{GITHUB_WEB}/login/oauth/access_token").mock(
        return_value=Response(200, json={"access_token": "test-user-token", "token_type": "bearer"})
    )
    router.get(f"{GITHUB_API}/user").mock(
        return_value=Response(
            200,
            json={"login": "maria.silva", "name": "Maria Silva", "avatar_url": "https://x/a.png"},
        )
    )
    router.post(f"{GITHUB_API}/app/installations/999/access_tokens").mock(
        return_value=Response(201, json={"token": "test-installation-token"})
    )
    router.get(f"{GITHUB_API}/repos/cte-zl-ifrn/central-ajuda/collaborators/maria.silva/permission").mock(
        return_value=Response(200, json={"permission": permission})
    )


@respx.mock
def test_callback_with_valid_state_creates_session(client):
    _mock_successful_github(respx)

    login_response = client.get("/auth/login", follow_redirects=False)
    state = login_response.cookies["portal_oauth_state"]
    client.cookies.set("portal_oauth_state", state)

    response = client.get(
        "/auth/callback",
        params={"code": "abc123", "state": state},
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["location"] == "http://localhost:5173"
    assert "portal_session" in response.cookies


@respx.mock
def test_callback_with_missing_state_cookie_is_rejected(client):
    _mock_successful_github(respx)

    response = client.get(
        "/auth/callback",
        params={"code": "abc123", "state": "whatever"},
        follow_redirects=False,
    )

    assert response.status_code == 400
    body = response.json()
    assert body["error"] == "invalid_oauth_state"
    assert "portal_session" not in response.cookies


@respx.mock
def test_callback_with_mismatched_state_is_rejected(client):
    _mock_successful_github(respx)

    login_response = client.get("/auth/login", follow_redirects=False)
    state = login_response.cookies["portal_oauth_state"]
    client.cookies.set("portal_oauth_state", state)

    response = client.get(
        "/auth/callback",
        params={"code": "abc123", "state": "a-different-state-value"},
        follow_redirects=False,
    )

    assert response.status_code == 400
    assert response.json()["error"] == "invalid_oauth_state"
