from extensions import db
from models import User


def _login(client, email, password="password123"):
    client.post("/api/auth/register", json={"email": email, "password": password})
    return client.post("/api/auth/login",
                       json={"email": email, "password": password}).get_json()["access_token"]


def _admin_token(client, app):
    client.post("/api/auth/register",
                json={"email": "admin@t.com", "password": "admin123"})
    tok = client.post("/api/auth/login",
                      json={"email": "admin@t.com",
                            "password": "admin123"}).get_json()["access_token"]
    with app.app_context():
        u = User.query.filter_by(email="admin@t.com").first()
        u.role = "admin"
        db.session.commit()
    return client.post("/api/auth/login",
                       json={"email": "admin@t.com",
                             "password": "admin123"}).get_json()["access_token"]


def test_flow_register_login_purchase_tickets(client):
    token = _login(client, "u@t.com")
    r = client.post("/api/purchase",
                    headers={"Authorization": f"Bearer {token}"},
                    json={"concert_id": 1, "quantity": 2})
    assert r.status_code == 201
    assert r.get_json()["tickets_created"] == 2
    tickets = client.get("/api/user/tickets",
                         headers={"Authorization": f"Bearer {token}"}).get_json()
    assert len(tickets) == 2
    assert all(t["used"] is False for t in tickets)


def test_flow_stock_insufficient_no_tickets(client):
    token = _login(client, "u@t.com")
    before_stock = client.get("/api/concerts").get_json()["concerts"][0]["stock"]
    r = client.post("/api/purchase",
                    headers={"Authorization": f"Bearer {token}"},
                    json={"concert_id": 1, "quantity": 9999})
    assert r.status_code == 400
    after_stock = client.get("/api/concerts").get_json()["concerts"][0]["stock"]
    assert after_stock == before_stock
    tickets = client.get("/api/user/tickets",
                         headers={"Authorization": f"Bearer {token}"}).get_json()
    assert tickets == []


def test_flow_isolation_between_users(client):
    t1 = _login(client, "a@t.com")
    client.post("/api/purchase",
                headers={"Authorization": f"Bearer {t1}"},
                json={"concert_id": 1, "quantity": 1})
    client.post("/api/auth/register",
                json={"email": "b@t.com", "password": "password123"})
    t2 = client.post("/api/auth/login",
                     json={"email": "b@t.com",
                           "password": "password123"}).get_json()["access_token"]
    assert client.get("/api/user/purchases",
                      headers={"Authorization": f"Bearer {t2}"}).get_json() == []
    assert client.get("/api/user/tickets",
                      headers={"Authorization": f"Bearer {t2}"}).get_json() == []


def test_flow_validate_and_double_scan(client, app):
    utok, code = None, None
    utok = _login(client, "u@t.com")
    client.post("/api/purchase",
                headers={"Authorization": f"Bearer {utok}"},
                json={"concert_id": 1, "quantity": 1})
    code = client.get("/api/user/tickets",
                      headers={"Authorization": f"Bearer {utok}"}).get_json()[0]["code"]
    atok = _admin_token(client, app)
    r1 = client.post("/api/admin/tickets/validate",
                     headers={"Authorization": f"Bearer {atok}"},
                     json={"code": code})
    assert r1.status_code == 200
    r2 = client.post("/api/admin/tickets/validate",
                     headers={"Authorization": f"Bearer {atok}"},
                     json={"code": code})
    assert r2.status_code == 409


def test_flow_profile_roundtrip(client):
    token = _login(client, "u@t.com")
    r = client.put("/api/user/me",
                   headers={"Authorization": f"Bearer {token}"},
                   json={"nombre": "Ana", "apellido": "Test"})
    assert r.status_code == 200
    r2 = client.get("/api/user/me",
                    headers={"Authorization": f"Bearer {token}"})
    assert r2.get_json()["nombre"] == "Ana"
    assert r2.get_json()["apellido"] == "Test"


def test_flow_search_and_detail(client):
    r = client.get("/api/concerts?q=duki")
    assert r.status_code == 200
    data = r.get_json()
    assert data["total"] >= 1
    cid = data["concerts"][0]["id"]
    r2 = client.get(f"/api/concerts/{cid}")
    assert r2.status_code == 200
    assert r2.get_json()["id"] == cid