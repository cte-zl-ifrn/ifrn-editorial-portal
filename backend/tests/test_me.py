from conftest import set_session_cookie


def test_me_without_session_is_unauthenticated(client):
    response = client.get("/api/me")

    assert response.status_code == 401
    assert response.json()["error"] == "unauthenticated"


def test_me_with_authorized_session(client, settings):
    set_session_cookie(client, settings, authorized=True, permission="write")

    response = client.get("/api/me")

    assert response.status_code == 200
    body = response.json()
    assert body["user"]["login"] == "maria.silva"
    assert body["authorized"] is True
    assert body["repository_permission"] == "write"


def test_me_with_unauthorized_session(client, settings):
    set_session_cookie(client, settings, authorized=False, permission="read")

    response = client.get("/api/me")

    assert response.status_code == 200
    body = response.json()
    assert body["authorized"] is False
    assert body["repository_permission"] == "read"
