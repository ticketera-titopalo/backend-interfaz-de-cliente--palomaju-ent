from extensions import db
from models import User


def _seed_admin(client, app):
    client.post("/api/auth/register",
                json={"email": "admin@t.com", "password": "admin123"})
    token = client.post("/api/auth/login",
                        json={"email": "admin@t.com",
                              "password": "admin123"}).get_json()["access_token"]
    with app.app_context():
        u = User.query.filter_by(email="admin@t.com").first()
        u.role = "admin"
        db.session.commit()
    return token


def _user_token(client, email="u@t.com", quantity=1):
    client.post("/api/auth/register",
                json={"email": email, "password": "password123"})
    token = client.post("/api/auth/login",
                       json={"email": email,
                             "password": "password123"}).get_json()["access_token"]
    client.post("/api/purchase",
               headers={"Authorization": f"Bearer {token}"},
               json={"concert_id": 1, "quantity": quantity})
    code = client.get("/api/user/tickets",
                     headers={"Authorization": f"Bearer {token}"}).get_json()[0]["code"]
    return token, code


def test_validate_ok(client, app):
    utok, code = _user_token(client)
    atok = _seed_admin(client, app)
    r = client.post("/api/admin/tickets/validate",
                    headers={"Authorization": f"Bearer {atok}"},
                    json={"code": code})
    assert r.status_code == 200
    body = r.get_json()
    assert body["used"] is True
    assert body["propietario"]["email"] == "u@t.com"


def test_double_scan(client, app):
    utok, code = _user_token(client)
    atok = _seed_admin(client, app)
    r1 = client.post("/api/admin/tickets/validate",
                     headers={"Authorization": f"Bearer {atok}"},
                     json={"code": code})
    r2 = client.post("/api/admin/tickets/validate",
                     headers={"Authorization": f"Bearer {atok}"},
                     json={"code": code})
    assert r1.status_code == 200
    assert r2.status_code == 409


def test_client_forbidden(client, app):
    utok, code = _user_token(client)
    r = client.post("/api/admin/tickets/validate",
                    headers={"Authorization": f"Bearer {utok}"},
                    json={"code": code})
    assert r.status_code == 403


def test_no_token(client):
    r = client.post("/api/admin/tickets/validate",
                    json={"code": "TKT-XXXXXX"})
    assert r.status_code == 401


def test_fake_code(client, app):
    atok = _seed_admin(client, app)
    r = client.post("/api/admin/tickets/validate",
                    headers={"Authorization": f"Bearer {atok}"},
                    json={"code": "TKT-ZZZ999"})
    assert r.status_code == 404
