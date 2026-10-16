def test_search_by_name_case_insensitive(client):
    r = client.get("/api/concerts?q=duki")
    assert r.status_code == 200
    data = r.get_json()
    assert data["total"] >= 1
    assert all("Duki" in c["name"] for c in data["concerts"])
    # case insensitive
    r2 = client.get("/api/concerts?q=DUKI")
    assert r2.get_json()["total"] == data["total"]


def test_search_by_description(client):
    r = client.get("/api/concerts?q=estadio")
    assert r.status_code == 200
    assert r.get_json()["total"] >= 1


def test_filter_by_date_range(client):
    r = client.get("/api/concerts?fecha_desde=2025-03-01&fecha_hasta=2025-04-30")
    assert r.status_code == 200
    data = r.get_json()
    assert data["total"] >= 1
    for c in data["concerts"]:
        assert "2025-03" <= c["date"] <= "2025-04-30"


def test_order_by_price_asc(client):
    r = client.get("/api/concerts?order=precio_asc&limit=100")
    assert r.status_code == 200
    prices = [c["price"] for c in r.get_json()["concerts"]]
    assert prices == sorted(prices)


def test_order_by_price_desc(client):
    r = client.get("/api/concerts?order=precio_desc&limit=100")
    assert r.status_code == 200
    prices = [c["price"] for c in r.get_json()["concerts"]]
    assert prices == sorted(prices, reverse=True)


def test_order_by_date_desc(client):
    r = client.get("/api/concerts?order=fecha_desc&limit=100")
    assert r.status_code == 200
    dates = [c["date"] for c in r.get_json()["concerts"]]
    assert dates == sorted(dates, reverse=True)


def test_pagination_no_overlap(client):
    p1 = client.get("/api/concerts?page=1&limit=3").get_json()["concerts"]
    p2 = client.get("/api/concerts?page=2&limit=3").get_json()["concerts"]
    ids1 = {c["id"] for c in p1}
    ids2 = {c["id"] for c in p2}
    assert ids1.isdisjoint(ids2)
    assert len(p1) == 3


def test_pagination_total_pages(client):
    r = client.get("/api/concerts?page=1&limit=3")
    data = r.get_json()
    assert data["page"] == 1
    assert data["limit"] == 3
    import math
    assert data["total_pages"] == (data["total"] + 2) // 3


def test_invalid_order(client):
    r = client.get("/api/concerts?order=foo")
    assert r.status_code == 400


def test_invalid_page(client):
    r = client.get("/api/concerts?page=0")
    assert r.status_code == 400
    r2 = client.get("/api/concerts?page=abc")
    assert r2.status_code == 400


def test_invalid_limit(client):
    r = client.get("/api/concerts?limit=0")
    assert r.status_code == 400
    r2 = client.get("/api/concerts?limit=101")
    assert r2.status_code == 400


def test_invalid_date(client):
    r = client.get("/api/concerts?fecha_desde=30-10-2025")
    assert r.status_code == 400


def test_no_results(client):
    r = client.get("/api/concerts?q=__nope__xyz")
    assert r.status_code == 200
    data = r.get_json()
    assert data["concerts"] == []
    assert data["total"] == 0
    assert data["total_pages"] == 0


def test_default_order_and_limit(client):
    r = client.get("/api/concerts")
    assert r.status_code == 200
    data = r.get_json()
    assert data["page"] == 1
    assert data["limit"] == 12