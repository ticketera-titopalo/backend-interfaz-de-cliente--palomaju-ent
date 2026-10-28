import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")

from flask import Flask
from flask_cors import CORS

from extensions import db, jwt
import models
from routes import register_blueprints


def _configure_jwt(app):
    # SEC: la clave viene de entorno (sin fallback).
    app.config["JWT_SECRET_KEY"] = os.environ["JWT_SECRET_KEY"]
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = int(
        os.environ.get("JWT_ACCESS_TOKEN_EXPIRES", 900))
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = int(
        os.environ.get("JWT_REFRESH_TOKEN_EXPIRES", 604800))
    jwt.init_app(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        from models import RevokedToken
        return RevokedToken.query.filter_by(
            jti=jwt_payload.get("jti")).first() is not None


def _database_uri():
    database_uri = os.environ.get("DATABASE_URI")
    if database_uri:
        return database_uri
    user = os.environ["MYSQL_USER"]
    password = os.environ["MYSQL_PASSWORD"]
    db_name = os.environ["MYSQL_DATABASE"]
    return f"mysql+pymysql://{user}:{password}@localhost:3306/{db_name}"


def _configure_cors(app):
    origins = [o.strip() for o in os.environ["FRONTEND_URL"].split(",")
               if o.strip()]
    if not origins:
        raise RuntimeError("FRONTEND_URL no definido o vacío")
    CORS(app, resources={r"/api/*": {"origins": origins}})


def create_app():
    app = Flask(__name__)
    _configure_jwt(app)
    app.config["SQLALCHEMY_DATABASE_URI"] = _database_uri()
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    _configure_cors(app)

    register_blueprints(app)
    from errors import register_error_handlers
    register_error_handlers(app)

    with app.app_context():
        db.create_all()
        _seed_concerts_if_empty()
        _migrate_user_profile_columns()

    return app


def _migrate_user_profile_columns():
    from sqlalchemy import text
    if db.session.bind is not None and db.session.bind.dialect.name != "mysql":
        return
    cols = ["nombre VARCHAR(80) NULL", "apellido VARCHAR(80) NULL",
            "dni VARCHAR(20) NULL", "telefono VARCHAR(30) NULL"]
    # NOTE: UNIQUE index on dni handled separately; keep simple.
    statements = [f"ALTER TABLE users ADD COLUMN {col}" for col in cols] + \
        ["CREATE UNIQUE INDEX uq_users_dni ON users(dni)"]
    for stmt in statements:
        try:
            db.session.execute(text(stmt))
            db.session.commit()
        except Exception:
            db.session.rollback()


SEED_CONCERTS = [
    {"name": "Duki - ADA Tour",
     "description": "El trap argentino llega al estadio.",
     "date": "2024-12-10", "price": 45000.0, "stock": 100,
     "image_url": "https://via.placeholder.com/150"},
    {"name": "Wos - Descartable",
     "description": "Presentación del nuevo disco.",
     "date": "2024-11-15", "price": 35000.0, "stock": 50,
     "image_url": "https://via.placeholder.com/150"},
    {"name": "Babasónicos",
     "description": "Show íntimo en el Luna Park.",
     "date": "2024-10-20", "price": 28000.0, "stock": 20,
     "image_url": "https://via.placeholder.com/150"},
    {"name": "Charly García",
     "description": "Histórico en el Colón.",
     "date": "2025-03-10", "price": 70000.0, "stock": 30,
     "image_url": "https://via.placeholder.com/150"},
    {"name": "Los Fabulosos Cadillacs",
     "description": "Regreso a los escenarios.",
     "date": "2025-04-05", "price": 50000.0, "stock": 80,
     "image_url": "https://via.placeholder.com/150"},
    {"name": "Fito Páez",
     "description": "Un aliento en el firmamento.",
     "date": "2025-05-20", "price": 42000.0, "stock": 60,
     "image_url": "https://via.placeholder.com/150"},
    {"name": "La Renga",
     "description": "Obras sanitarias.",
     "date": "2025-06-18", "price": 38000.0, "stock": 40,
     "image_url": "https://via.placeholder.com/150"},
    {"name": "Usted Señalemelo",
     "description": "Playa gigante tour.",
     "date": "2025-07-22", "price": 30000.0, "stock": 100,
     "image_url": "https://via.placeholder.com/150"},
    {"name": "Indio Solari",
     "description": "El último show.",
     "date": "2025-08-30", "price": 95000.0, "stock": 10,
     "image_url": "https://via.placeholder.com/150"},
    {"name": "Soda Stereo",
     "description": "Gracias por otros 20 años.",
     "date": "2025-09-15", "price": 120000.0, "stock": 25,
     "image_url": "https://via.placeholder.com/150"},
]


def _seed_concerts_if_empty():
    from models import Concert
    if Concert.query.count() != 0:
        return
    db.session.bulk_save_objects(
        [Concert(**c) for c in SEED_CONCERTS])
    db.session.commit()


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5000)
