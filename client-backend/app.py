import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")

from flask import Flask
from flask_cors import CORS

from extensions import db, jwt
import models
from routes import register_blueprints


def create_app():
    app = Flask(__name__)
    # SEC: la clave viene de entorno (sin fallback).
    app.config["JWT_SECRET_KEY"] = os.environ["JWT_SECRET_KEY"]
    jwt.init_app(app)

    database_uri = os.environ.get("DATABASE_URI")
    if database_uri:
        app.config["SQLALCHEMY_DATABASE_URI"] = database_uri
    else:
        user = os.environ["MYSQL_USER"]
        password = os.environ["MYSQL_PASSWORD"]
        db_name = os.environ["MYSQL_DATABASE"]
        app.config["SQLALCHEMY_DATABASE_URI"] = (
            f"mysql+pymysql://{user}:{password}@localhost:3306/{db_name}"
        )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    CORS(app, resources={r"/api/*": {
        "origins": os.environ["FRONTEND_URL"],
    }})

    register_blueprints(app)

    with app.app_context():
        db.create_all()
        _seed_concerts_if_empty()
        _migrate_user_profile_columns()

    return app


def _migrate_user_profile_columns():
    from sqlalchemy import text
    cols = ["nombre VARCHAR(80) NULL", "apellido VARCHAR(80) NULL",
            "dni VARCHAR(20) NULL", "telefono VARCHAR(30) NULL"]
    # NOTE: UNIQUE index on dni handled separately; keep simple.
    if db.session.bind is not None and db.session.bind.dialect.name != "mysql":
        return
    for col in ["nombre VARCHAR(80) NULL", "apellido VARCHAR(80) NULL",
                "dni VARCHAR(20) NULL", "telefono VARCHAR(30) NULL"]:
        try:
            db.session.execute(text(f"ALTER TABLE users ADD COLUMN {col}"))
            db.session.commit()
        except Exception:
            db.session.rollback()
    # unique index on dni (best effort)
    try:
        db.session.execute(text("CREATE UNIQUE INDEX uq_users_dni ON users(dni)"))
        db.session.commit()
    except Exception:
        db.session.rollback()


def _seed_concerts_if_empty():
    from models import Concert
    if Concert.query.count() != 0:
        return
    db.session.bulk_save_objects([
        Concert(name="Duki - ADA Tour",
                description="El trap argentino llega al estadio.",
                date="2024-12-10", price=45000.0, stock=100,
                image_url="https://via.placeholder.com/150"),
        Concert(name="Wos - Descartable",
                description="Presentación del nuevo disco.",
                date="2024-11-15", price=35000.0, stock=50,
                image_url="https://via.placeholder.com/150"),
        Concert(name="Babasónicos",
                description="Show íntimo en el Luna Park.",
                date="2024-10-20", price=28000.0, stock=20,
                image_url="https://via.placeholder.com/150"),
    ])
    db.session.commit()


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5000)
