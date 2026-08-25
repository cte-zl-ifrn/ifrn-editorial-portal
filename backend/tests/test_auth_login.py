from urllib.parse import parse_qs, urlparse


def test_login_redirects_to_github_with_state(client):
    response = client.get("/auth/login", follow_redirects=False)

    assert response.status_code == 302
    location = response.headers["location"]
    parsed = urlparse(location)
    assert parsed.netloc == "github.com"
    assert parsed.path == "/login/oauth/authorize"

    query = parse_qs(parsed.query)
    assert query["client_id"] == ["test-client-id"]
    assert "state" in query

    state_cookie = response.cookies.get("portal_oauth_state")
    assert state_cookie == query["state"][0]
