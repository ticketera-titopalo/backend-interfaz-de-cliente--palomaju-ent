def test_404_standard(client):
    r = client.get("/api/nope")
    assert r.status_code == 404
    body = r.get_json()
    assert "message" in body


def test_405_standard(client):
    r = client.post("/api/status")
    assert r.status_code == 405
    body = r.get_json()
    assert "message" in body


def test_500_no_leak(client, app):
    @app.route("/boom")
    def boom():
        raise ValueError("secret detail should not leak")

    r = client.get("/boom")
    assert r.status_code == 500
    body = r.get_json()
    assert "error" in body
    assert "secret detail" not in str(body)
    assert "traceback" not in str(body).lower()


def test_status_version(client):
    r = client.get("/api/status")
    assert r.status_code == 200
    body = r.get_json()
    assert body["database"] == "connected"
    assert "version" in body
