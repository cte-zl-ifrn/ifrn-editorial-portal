from conftest import set_session_cookie


def test_logout_clears_session_cookie(client, settings):
    set_session_cookie(client, settings, authorized=True)

    response = client.post("/auth/logout")

    assert response.status_code == 204
    set_cookie_header = response.headers.get("set-cookie", "")
    assert settings.session_cookie_name in set_cookie_header


def test_logout_without_session_is_idempotent(client):
    response = client.post("/auth/logout")

    assert response.status_code == 204
