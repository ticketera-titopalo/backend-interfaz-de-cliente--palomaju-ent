def test_smoke_routes(client):
    assert client.get("/api/status").status_code == 200
    assert client.get("/api/concerts").status_code == 200
    assert client.get("/api/concerts/1").status_code == 200
    assert client.get("/api/concerts/999").status_code == 404

    # sin token devuelve 401 en los protegidos
    assert client.get("/api/user/tickets").status_code == 401
    assert client.get("/api/user/purchases").status_code == 401
    assert client.post("/api/purchase", json={}).status_code == 401
    assert client.post("/api/admin/tickets/validate",
                       json={"code": "X"}).status_code == 401
