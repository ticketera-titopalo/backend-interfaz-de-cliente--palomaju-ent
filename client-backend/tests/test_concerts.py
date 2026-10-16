def test_concerts_list(client):
    r = client.get("/api/concerts")
    assert r.status_code == 200
    data = r.get_json()
    assert isinstance(data, dict)
    assert "concerts" in data and isinstance(data["concerts"], list)
    assert len(data["concerts"]) >= 3
    assert "total" in data and "page" in data and "limit" in data
    assert "total_pages" in data


def test_detail_ok(client):
    r = client.get("/api/concerts/1")
    assert r.status_code == 200
    data = r.get_json()
    assert data["name"] == "Duki - ADA Tour"
    assert "stock" in data and "price" in data


def test_detail_not_found(client):
    r = client.get("/api/concerts/999")
    assert r.status_code == 404
    assert r.get_json()["message"] == "Concierto no encontrado"


def test_detail_non_numeric(client):
    r = client.get("/api/concerts/abc")
    assert r.status_code == 404


def test_detail_no_token_ok(client):
    # Detalle de concierto es público.
    assert client.get("/api/concerts/2").status_code == 200


def test_status(client):
    r = client.get("/api/status")
    assert r.status_code == 200
    assert r.get_json()["database"] == "connected"
