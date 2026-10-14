def _login_and_buy(client, email="u@t.com", quantity=3):
    client.post("/api/auth/register",
                json={"email": email, "password": "password123"})
    token = client.post("/api/auth/login",
                       json={"email": email,
                             "password": "password123"}).get_json()["access_token"]
    client.post("/api/purchase",
               headers={"Authorization": f"Bearer {token}"},
               json={"concert_id": 1, "quantity": quantity})
    return token


def test_emission_count(client):
    token = _login_and_buy(client, quantity=3)
    r = client.get("/api/user/tickets",
                   headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert len(r.get_json()) == 3


def test_codes_unique(client):
    token = _login_and_buy(client, quantity=3)
    codes = [t["code"] for t in
             client.get("/api/user/tickets",
                        headers={"Authorization": f"Bearer {token}"}).get_json()]
    assert len(set(codes)) == len(codes) == 3
    assert all(c.startswith("TKT-") for c in codes)


def test_tickets_empty(client):
    client.post("/api/auth/register",
                json={"email": "u@t.com", "password": "password123"})
    token = client.post("/api/auth/login",
                       json={"email": "u@t.com",
                             "password": "password123"}).get_json()["access_token"]
    r = client.get("/api/user/tickets",
                   headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.get_json() == []


def test_tickets_isolation(client):
    token_a = _login_and_buy(client, "a@t.com", 2)
    client.post("/api/auth/register",
                json={"email": "b@t.com", "password": "password123"})
    token_b = client.post("/api/auth/login",
                         json={"email": "b@t.com",
                               "password": "password123"}).get_json()["access_token"]
    r = client.get("/api/user/tickets",
                   headers={"Authorization": f"Bearer {token_b}"})
    assert r.status_code == 200
    assert r.get_json() == []
    # sanity: a has 2
    assert len(client.get("/api/user/tickets",
                       headers={"Authorization": f"Bearer {token_a}"}).get_json()) == 2


def test_purchase_tickets_403(client):
    token_a = _login_and_buy(client, "a@t.com", 1)
    purchases = client.get("/api/user/purchases",
                          headers={"Authorization": f"Bearer {token_a}"}).get_json()
    purchase_id = purchases[0]["id"]
    client.post("/api/auth/register",
                json={"email": "b@t.com", "password": "password123"})
    token_b = client.post("/api/auth/login",
                         json={"email": "b@t.com",
                               "password": "password123"}).get_json()["access_token"]
    r = client.get(f"/api/user/purchases/{purchase_id}/tickets",
                   headers={"Authorization": f"Bearer {token_b}"})
    assert r.status_code == 403
