"""Servicio de autenticacion y emision de tokens."""

from flask_jwt_extended import create_access_token
from extensions import db
from models import User


def register_user(email, password):
    if not email or not password:
        return None, "Email y contraseña son obligatorios", 400
    if len(password) < 8:
        return None, "La contraseña debe tener al menos 8 caracteres", 400
    email_clean = (email or "").lower().strip()
    if User.query.filter_by(email=email_clean).first():
        return None, "El correo ya está registrado", 409
    user = User(email=email_clean)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user, None, 201


def authenticate_user(email, password):
    if not email or not password:
        return None, "Credenciales inválidas"
    user = User.query.filter_by(email=(email or "").lower().strip()).first()
    if not user or not user.check_password(password):
        return None, "Credenciales inválidas"
    token = create_access_token(identity=str(user.id))
    return user, token
