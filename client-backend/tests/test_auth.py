def _register(client, email="u@t.com", password="password123"):
    return client.post("/api/auth/register",
                      json={"email": email, "password": password})


def test_register_ok(client):
    r = _register(client)
    assert r.status_code == 201
    assert r.get_json()["user"]["role"] == "client"


def test_register_duplicate(client):
    _register(client)
    r = _register(client)
    assert r.status_code == 409


def test_register_password_too_short(client):
    r = client.post("/api/auth/register",
                    json={"email": "u@t.com", "password": "123"})
    assert r.status_code == 400


def test_login_invalid(client):
    _register(client)
    r = client.post("/api/auth/login",
                    json={"email": "u@t.com", "password": "wrong"})
    assert r.status_code == 401


def test_missing_token(client):
    r = client.get("/api/user/tickets")
    assert r.status_code == 401


def test_invalid_token(client):
    r = client.get("/api/user/tickets",
                   headers={"Authorization": "Bearer not.a.token"})
    assert r.status_code in (401, 422)
