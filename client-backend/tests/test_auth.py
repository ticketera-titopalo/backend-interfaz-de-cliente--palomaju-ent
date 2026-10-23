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


def test_register_invalid_email(client):
    r = client.post("/api/auth/register",
                    json={"email": "notanemail", "password": "password123"})
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


def test_refresh_token_emits_access(client):
    _register(client)
    login = client.post("/api/auth/login", json={
        "email": "u@t.com", "password": "password123"
    }).get_json()
    refresh = login["refresh_token"]
    assert refresh
    r = client.post("/api/auth/refresh",
                    headers={"Authorization": f"Bearer {refresh}"})
    assert r.status_code == 200
    assert "access_token" in r.get_json()


def test_refresh_requires_refresh_token(client):
    _register(client)
    access = client.post("/api/auth/login", json={
        "email": "u@t.com", "password": "password123"
    }).get_json()["access_token"]
    r = client.post("/api/auth/refresh",
                    headers={"Authorization": f"Bearer {access}"})
    assert r.status_code in (401, 422)


def test_logout_revokes_refresh(client):
    _register(client)
    login = client.post("/api/auth/login", json={
        "email": "u@t.com", "password": "password123"
    }).get_json()
    refresh = login["refresh_token"]
    access = login["access_token"]
    r = client.post("/api/auth/logout",
                    headers={"Authorization": f"Bearer {access}"},
                    json={"refresh_token": refresh})
    assert r.status_code == 200
    r2 = client.post("/api/auth/refresh",
                     headers={"Authorization": f"Bearer {refresh}"})
    assert r2.status_code in (401, 422)


def test_email_normalized(client):
    client.post("/api/auth/register",
                json={"email": "  User@Example.COM ", "password": "password123"})
    r = client.post("/api/auth/login",
                    json={"email": "user@example.com", "password": "password123"})
    assert r.status_code == 200