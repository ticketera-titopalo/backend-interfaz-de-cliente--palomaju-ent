def _login(client, email="u@t.com", password="password123"):
    client.post("/api/auth/register",
                json={"email": email, "password": password})
    r = client.post("/api/auth/login",
                    json={"email": email, "password": password})
    return r.get_json()["access_token"]


def test_purchase_ok(client):
    token = _login(client)
    r = client.post("/api/purchase",
                    headers={"Authorization": f"Bearer {token}"},
                    json={"concert_id": 1, "quantity": 2})
    assert r.status_code == 201
    body = r.get_json()
    assert body["tickets_created"] == 2
    assert body["quantity"] == 2


def test_purchase_stock_insufficient(client):
    token = _login(client)
    r = client.post("/api/purchase",
                    headers={"Authorization": f"Bearer {token}"},
                    json={"concert_id": 1, "quantity": 9999})
    assert r.status_code == 400


def test_purchase_quantity_invalid(client):
    token = _login(client)
    for q in (0, -1, 1.5, "a"):
        r = client.post("/api/purchase",
                        headers={"Authorization": f"Bearer {token}"},
                        json={"concert_id": 1, "quantity": q})
        assert r.status_code == 400


def test_purchase_concert_missing(client):
    token = _login(client)
    r = client.post("/api/purchase",
                    headers={"Authorization": f"Bearer {token}"},
                    json={"concert_id": 999, "quantity": 1})
    assert r.status_code == 404


def test_purchases_only_own(client):
    t1 = _login(client, "a@t.com")
    client.post("/api/purchase",
                headers={"Authorization": f"Bearer {t1}"},
                json={"concert_id": 1, "quantity": 1})
    # second user with no purchases
    client.post("/api/auth/register",
                json={"email": "b@t.com", "password": "password123"})
    t2 = client.post("/api/auth/login",
                     json={"email": "b@t.com", "password": "password123"}).get_json()["access_token"]
    r = client.get("/api/user/purchases",
                   headers={"Authorization": f"Bearer {t2}"})
    assert r.status_code == 200
    assert r.get_json() == []
