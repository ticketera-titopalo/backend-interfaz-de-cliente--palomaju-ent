from extensions import db
from models import User


def _admin_headers(client, app):
    client.post(
        "/api/auth/register",
        json={"email": "admin_c@t.com", "password": "password123"},
    )
    with app.app_context():
        u = User.query.filter_by(email="admin_c@t.com").first()
        u.role = "admin"
        db.session.commit()
    tok = client.post(
        "/api/auth/login",
        json={"email": "admin_c@t.com", "password": "password123"},
    ).get_json()["access_token"]
    return {"Authorization": f"Bearer {tok}"}


def test_admin_concerts_crud_and_restock(client, app):
    headers = _admin_headers(client, app)

    r_create = client.post(
        "/api/admin/concerts",
        headers=headers,
        json={
            "name": "Show Prueba",
            "date": "2026-12-01",
            "price": 15000,
            "stock": 50,
            "description": "Desc",
            "image_url": "http://img.test/a.jpg",
        },
    )
    assert r_create.status_code == 201
    cid = r_create.get_json()["id"]

    assert (
        client.post("/api/admin/concerts", headers=headers, json={"name": ""}).status_code
        == 400
    )
    assert (
        client.post(
            "/api/admin/concerts", headers=headers, json={"name": "A", "date": ""}
        ).status_code
        == 400
    )
    assert (
        client.post(
            "/api/admin/concerts",
            headers=headers,
            json={"name": "A", "date": "2026-12-01", "price": -5},
        ).status_code
        == 400
    )
    assert (
        client.post(
            "/api/admin/concerts",
            headers=headers,
            json={"name": "A", "date": "2026-12-01", "price": 10, "stock": -1},
        ).status_code
        == 400
    )
    assert (
        client.post(
            "/api/admin/concerts",
            headers=headers,
            json={"name": "A", "date": "2026-12-01", "price": True},
        ).status_code
        == 400
    )

    r_upd = client.put(
        f"/api/admin/concerts/{cid}",
        headers=headers,
        json={
            "name": "Show Editado",
            "description": "Nueva desc",
            "date": "2026-12-05",
            "price": 20000,
            "stock": 60,
            "image_url": "http://img.test/b.jpg",
        },
    )
    assert r_upd.status_code == 200
    assert r_upd.get_json()["name"] == "Show Editado"
    assert (
        client.put(
            "/api/admin/concerts/9999", headers=headers, json={"name": "X"}
        ).status_code
        == 404
    )
    assert (
        client.put(
            f"/api/admin/concerts/{cid}", headers=headers, json={"name": ""}
        ).status_code
        == 400
    )
    assert (
        client.put(
            f"/api/admin/concerts/{cid}", headers=headers, json={"price": "no-num"}
        ).status_code
        == 400
    )
    assert (
        client.put(
            f"/api/admin/concerts/{cid}", headers=headers, json={"stock": -3}
        ).status_code
        == 400
    )

    r_stock = client.post(
        f"/api/admin/concerts/{cid}/stock", headers=headers, json={"cantidad": 15}
    )
    assert r_stock.status_code == 200
    assert r_stock.get_json()["stock"] == 75
    assert (
        client.post(
            f"/api/admin/concerts/{cid}/stock", headers=headers, json={"cantidad": 0}
        ).status_code
        == 400
    )
    assert (
        client.post(
            "/api/admin/concerts/9999/stock", headers=headers, json={"cantidad": 5}
        ).status_code
        == 404
    )

    client.post(
        "/api/purchase", headers=headers, json={"concert_id": cid, "quantity": 1}
    )
    assert (
        client.delete(f"/api/admin/concerts/{cid}", headers=headers).status_code == 409
    )

    cid2 = client.post(
        "/api/admin/concerts",
        headers=headers,
        json={
            "name": "Borrable",
            "date": "2026-12-10",
            "price": 1000,
            "stock": 5,
        },
    ).get_json()["id"]
    assert (
        client.delete(f"/api/admin/concerts/{cid2}", headers=headers).status_code == 204
    )
    assert (
        client.delete("/api/admin/concerts/9999", headers=headers).status_code == 404
    )


def test_purchase_tickets_ok_and_404_and_invalid_concert_id(client):
    client.post(
        "/api/auth/register", json={"email": "buyer@t.com", "password": "password123"}
    )
    tok = client.post(
        "/api/auth/login", json={"email": "buyer@t.com", "password": "password123"}
    ).get_json()["access_token"]
    h = {"Authorization": f"Bearer {tok}"}

    assert (
        client.post(
            "/api/purchase", headers=h, json={"concert_id": "abc", "quantity": 1}
        ).status_code
        == 400
    )
    assert (
        client.post(
            "/api/purchase", headers=h, json={"concert_id": True, "quantity": 1}
        ).status_code
        == 400
    )

    p_id = client.post(
        "/api/purchase", headers=h, json={"concert_id": 1, "quantity": 2}
    ).get_json()["purchase_id"]
    r_ok = client.get(f"/api/user/purchases/{p_id}/tickets", headers=h)
    assert r_ok.status_code == 200
    assert len(r_ok.get_json()) == 2
    assert client.get("/api/user/purchases/9999/tickets", headers=h).status_code == 404

    assert (
        client.put("/api/user/me", headers=h, json={"dni": "1" * 21}).status_code == 400
    )