def _register_and_login(client, email="edge@t.com", password="password123"):
    client.post("/api/auth/register", json={"email": email, "password": password})
    res = client.post("/api/auth/login", json={"email": email, "password": password})
    return res.get_json()["access_token"]


def test_auth_edge_cases(client):
    assert (
        client.post(
            "/api/auth/register", json={"email": "invalido", "password": "password123"}
        ).status_code
        == 400
    )
    assert (
        client.post(
            "/api/auth/register", json={"email": "corto@t.com", "password": "123"}
        ).status_code
        == 400
    )

    _register_and_login(client, "dup@t.com")
    assert (
        client.post(
            "/api/auth/register", json={"email": "dup@t.com", "password": "password123"}
        ).status_code
        == 409
    )

    assert (
        client.post(
            "/api/auth/login", json={"email": "noexiste@t.com", "password": "password123"}
        ).status_code
        == 401
    )
    assert (
        client.post(
            "/api/auth/login", json={"email": "dup@t.com", "password": "wrongpassword"}
        ).status_code
        == 401
    )


def test_public_concerts_endpoints(client):
    res_list = client.get("/api/concerts")
    assert res_list.status_code == 200
    assert isinstance(res_list.get_json(), (list, dict))

    assert client.get("/api/concerts/1").status_code in (200, 404)
    assert client.get("/api/concerts/9999").status_code == 404


def test_user_profile_and_tickets_edge_cases(client):
    tok = _register_and_login(client, "profile@t.com")
    headers = {"Authorization": f"Bearer {tok}"}

    res_me = client.get("/api/user/me", headers=headers)
    assert res_me.status_code == 200
    assert res_me.get_json()["email"] == "profile@t.com"

    res_upd = client.put(
        "/api/user/me",
        headers=headers,
        json={"nombre": "Paloma", "apellido": "Juarez", "dni": "40123456"},
    )
    assert res_upd.status_code == 200
    upd_data = res_upd.get_json()
    assert upd_data["nombre"] == "Paloma"
    assert upd_data["apellido"] == "Juarez"
    assert upd_data["dni"] == "40123456"

    p_res = client.post(
        "/api/purchase", headers=headers, json={"concert_id": 1, "quantity": 1}
    )
    assert p_res.status_code == 201
    p_id = p_res.get_json()["purchase_id"]

    purchases_res = client.get("/api/user/purchases", headers=headers)
    assert purchases_res.status_code == 200
    assert len(purchases_res.get_json()) == 1

    tickets_res = client.get(f"/api/user/purchases/{p_id}/tickets", headers=headers)
    assert tickets_res.status_code == 200
    tickets_list = tickets_res.get_json()
    assert len(tickets_list) == 1
    assert "id" in tickets_list[0]

    assert client.get("/api/user/purchases/9999/tickets", headers=headers).status_code == 404


def test_purchase_validation_and_stock_limits(client):
    tok = _register_and_login(client, "stock@t.com")
    headers = {"Authorization": f"Bearer {tok}"}

    assert (
        client.post(
            "/api/purchase", headers=headers, json={"concert_id": 1, "quantity": 0}
        ).status_code
        == 400
    )
    assert (
        client.post(
            "/api/purchase", headers=headers, json={"concert_id": 9999, "quantity": 1}
        ).status_code
        == 404
    )
    assert (
        client.post(
            "/api/purchase", headers=headers, json={"concert_id": 1, "quantity": 999999}
        ).status_code
        == 400
    )


def test_admin_authorization_forbidden_for_regular_user(client):
    tok = _register_and_login(client, "regular@t.com")
    headers = {"Authorization": f"Bearer {tok}"}

    assert (
        client.post(
            "/api/admin/concerts",
            headers=headers,
            json={"name": "No Admin", "date": "2026-12-01", "price": 100, "stock": 10},
        ).status_code
        == 403
    )