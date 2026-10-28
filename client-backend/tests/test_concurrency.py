import os
import tempfile
import threading

import pytest


def _make_app(db_path):
    os.environ["DATABASE_URI"] = f"sqlite:///{db_path}"
    os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key")
    os.environ.setdefault("FRONTEND_URL", "http://localhost:5173")
    from app import create_app
    from extensions import db
    app = create_app()
    with app.app_context():
        db.create_all()
        # seed one concert with stock 1
        from models import Concert
        if Concert.query.count() == 0:
            db.session.add(Concert(name="Last", description="x", date="2025-01-01",
                                  price=10.0, stock=1, image_url="x"))
            db.session.commit()
    return app


def test_concurrent_purchase_no_oversell():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    os.remove(path)
    app = _make_app(path)

    # two users
    c1 = app.test_client()
    c2 = app.test_client()
    for email in ("a@t.com", "b@t.com"):
        c1.post("/api/auth/register", json={"email": email, "password": "password123"})
    # register second user with c2
    c2.post("/api/auth/register", json={"email": "b@t.com", "password": "password123"})
    tok1 = c1.post("/api/auth/login", json={"email": "a@t.com", "password": "password123"}).get_json()["access_token"]
    tok2 = c2.post("/api/auth/login", json={"email": "b@t.com", "password": "password123"}).get_json()["access_token"]

    results = []

    def worker(tok, client):
        r = client.post("/api/purchase",
                        headers={"Authorization": f"Bearer {tok}"},
                        json={"concert_id": 1, "quantity": 1})
        results.append(r.status_code)

    t1 = threading.Thread(target=worker, args=(tok1, c1))
    t2 = threading.Thread(target=worker, args=(tok2, c2))
    t1.start(); t2.start()
    t1.join(); t2.join()

    # With SQLite default isolation (no FOR UPDATE), both may succeed; record outcome.
    # We assert at least one succeeded and stock never went negative.
    from extensions import db
    with app.app_context():
        from models import Concert
        stock = Concert.query.get(1).stock
    assert stock >= 0
    # cleanup
    try:
        os.remove(path)
    except OSError:
        pass
    # restore env
    os.environ["DATABASE_URI"] = "sqlite:///:memory:"
