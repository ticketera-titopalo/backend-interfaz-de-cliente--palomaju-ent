from extensions import db
from models import User, Concert, Purchase


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
    return (client.post("/api/auth/login",
                        json={"email": "admin@t.com",
                              "password": "admin123"}).get_json()["access_token"])


def _client_token(client, email="client@t.com"):
    client.post("/api/auth/register",
                json={"email": email, "password": "password123"})
    return client.post("/api/auth/login",
                       json={"email": email,
                             "password": "password123"}).get_json()["access_token"]


def test_create_concert_admin(client, app):
    tok = _admin_token(client, app)
    r = client.post("/api/admin/concerts",
                    headers={"Authorization": f"Bearer {tok}"},
                    json={"name": "Rock", "date": "2026-01-01",
                          "price": 5000, "stock": 10,
                          "image_url": "x"})
    assert r.status_code == 201
    data = r.get_json()
    assert data["name"] == "Rock"
    assert data["stock"] == 10
    return data["id"]


def test_create_price_invalid(client, app):
    tok = _admin_token(client, app)
    r = client.post("/api/admin/concerts",
                    headers={"Authorization": f"Bearer {tok}"},
                    json={"name": "X", "date": "2026-01-01", "price": 0, "stock": 1})
    assert r.status_code == 400


def test_create_missing_name(client, app):
    tok = _admin_token(client, app)
    r = client.post("/api/admin/concerts",
                    headers={"Authorization": f"Bearer {tok}"},
                    json={"date": "2026-01-01", "price": 10, "stock": 1})
    assert r.status_code == 400


def test_update_concert(client, app):
    tok = _admin_token(client, app)
    c = client.post("/api/admin/concerts",
                    headers={"Authorization": f"Bearer {tok}"},
                    json={"name": "X", "date": "2026-01-01",
                          "price": 10, "stock": 1}).get_json()
    r = client.put(f"/api/admin/concerts/{c['id']}",
                   headers={"Authorization": f"Bearer {tok}"},
                   json={"name": "X2", "stock": 5})
    assert r.status_code == 200
    assert r.get_json()["name"] == "X2"
    assert r.get_json()["stock"] == 5


def test_restock_accumulative(client, app):
    tok = _admin_token(client, app)
    c = client.post("/api/admin/concerts",
                    headers={"Authorization": f"Bearer {tok}"},
                    json={"name": "X", "date": "2026-01-01",
                          "price": 10, "stock": 1}).get_json()
    before = c["stock"]
    r = client.post(f"/api/admin/concerts/{c['id']}/stock",
                    headers={"Authorization": f"Bearer {tok}"},
                    json={"cantidad": 3})
    assert r.status_code == 200
    assert r.get_json()["stock"] == before + 3
    assert r.get_json()["agregado"] == 3


def test_restock_zero(client, app):
    tok = _admin_token(client, app)
    c = client.post("/api/admin/concerts",
                    headers={"Authorization": f"Bearer {tok}"},
                    json={"name": "X", "date": "2026-01-01",
                          "price": 10, "stock": 1}).get_json()
    r = client.post(f"/api/admin/concerts/{c['id']}/stock",
                    headers={"Authorization": f"Bearer {tok}"},
                    json={"cantidad": 0})
    assert r.status_code == 400


def test_delete_without_purchases(client, app):
    tok = _admin_token(client, app)
    c = client.post("/api/admin/concerts",
                    headers={"Authorization": f"Bearer {tok}"},
                    json={"name": "X", "date": "2026-01-01",
                          "price": 10, "stock": 1}).get_json()
    r = client.delete(f"/api/admin/concerts/{c['id']}",
                      headers={"Authorization": f"Bearer {tok}"})
    assert r.status_code == 204


def test_delete_with_purchases(client, app):
    admin_tok = _admin_token(client, app)
    c = client.post("/api/admin/concerts",
                    headers={"Authorization": f"Bearer {admin_tok}"},
                    json={"name": "X", "date": "2026-01-01",
                          "price": 10, "stock": 5}).get_json()
    cid = c["id"]
    client.post("/api/auth/register",
                json={"email": "u@t.com", "password": "password123"})
    utok = client.post("/api/auth/login",
                       json={"email": "u@t.com",
                             "password": "password123"}).get_json()["access_token"]
    client.post("/api/purchase",
               headers={"Authorization": f"Bearer {utok}"},
               json={"concert_id": cid, "quantity": 1})
    r = client.delete(f"/api/admin/concerts/{cid}",
                      headers={"Authorization": f"Bearer {admin_tok}"})
    assert r.status_code == 409


def test_admin_endpoints_forbidden_client(client, app):
    ctok = _client_token(client)
    r = client.post("/api/admin/concerts",
                    headers={"Authorization": f"Bearer {ctok}"},
                    json={"name": "X", "date": "d", "price": 1, "stock": 1})
    assert r.status_code == 403
    r = client.put("/api/admin/concerts/1",
                   headers={"Authorization": f"Bearer {ctok}"})
    assert r.status_code == 403
    r = client.delete("/api/admin/concerts/1",
                      headers={"Authorization": f"Bearer {ctok}"})
    assert r.status_code == 403
    r = client.post("/api/admin/concerts/1/stock",
                    headers={"Authorization": f"Bearer {ctok}"},
                    json={"cantidad": 1})
    assert r.status_code == 403


def test_admin_endpoints_no_token(client):
    assert client.post("/api/admin/concerts", json={}).status_code == 401
    assert client.put("/api/admin/concerts/1", json={}).status_code == 401
    assert client.delete("/api/admin/concerts/1").status_code == 401
    assert client.post("/api/admin/concerts/1/stock", json={}).status_code == 401


def test_delete_not_found(client, app):
    tok = _admin_token(client, app)
    r = client.delete("/api/admin/concerts/9999",
                      headers={"Authorization": f"Bearer {tok}"})
    assert r.status_code == 404
