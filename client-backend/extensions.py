"""Extensiones de Flask (islas separadas de la app para evitar ciclos de import)."""

from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
jwt = JWTManager()
