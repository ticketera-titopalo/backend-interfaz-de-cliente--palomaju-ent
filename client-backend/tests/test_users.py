def _login(client, email="u@t.com", password="password123"):
    client.post("/api/auth/register", json={"email": email, "password": password})
    r = client.post("/api/auth/login", json={"email": email, "password": password})
    return r.get_json()["access_token"]


def test_me_ok(client):
    token = _login(client)
    r = client.get("/api/user/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    body = r.get_json()
    assert "password_hash" not in body
    assert body["email"] == "u@t.com"
    assert "nombre" in body


def test_me_no_token(client):
    assert client.get("/api/user/me").status_code == 401


def test_put_profile_persists(client):
    token = _login(client)
    r = client.put("/api/user/me",
                   headers={"Authorization": f"Bearer {token}"},
                   json={"nombre": " Ana ", "apellido": "Test", "telefono": "12345"})
    assert r.status_code == 200
    assert r.get_json()["nombre"] == "Ana"  # trimmed
    r2 = client.get("/api/user/me", headers={"Authorization": f"Bearer {token}"})
    assert r2.get_json()["apellido"] == "Test"


def test_put_rejects_forbidden(client):
    token = _login(client)
    r = client.put("/api/user/me",
                   headers={"Authorization": f"Bearer {token}"},
                   json={"role": "admin"})
    assert r.status_code == 400


def test_put_password_rejected(client):
    token = _login(client)
    r = client.put("/api/user/me",
                   headers={"Authorization": f"Bearer {token}"},
                   json={"password": "newpass123"})
    assert r.status_code == 400


def test_put_dni_duplicate(client):
    t1 = _login(client, "a@t.com")
    # set dni for a
    client.put("/api/user/me",
               headers={"Authorization": f"Bearer {t1}"},
               json={"dni": "12345678"})
    # second user tries same dni
    t2 = _login(client, "b@t.com")
    r = client.put("/api/user/me",
                   headers={"Authorization": f"Bearer {t2}"},
                   json={"dni": "12345678"})
    assert r.status_code == 409


def test_put_name_too_long(client):
    token = _login(client)
    r = client.put("/api/user/me",
                   headers={"Authorization": f"Bearer {token}"},
                   json={"nombre": "x" * 81})
    assert r.status_code == 400
