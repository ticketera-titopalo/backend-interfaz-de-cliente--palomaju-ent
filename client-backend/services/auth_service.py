"""Servicio de autenticacion, emision y revocacion de tokens."""

import re

from flask_jwt_extended import create_access_token, create_refresh_token
from extensions import db
from models import User, RevokedToken


def _is_valid_email(email):
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email or ""))


def register_user(email, password):
    if not email or not password:
        return None, "Email y contraseña son obligatorios", 400
    if len(password) < 8:
        return None, "La contraseña debe tener al menos 8 caracteres", 400
    email_clean = (email or "").lower().strip()
    if not _is_valid_email(email_clean):
        return None, "Email inválido", 400
    if User.query.filter_by(email=email_clean).first():
        return None, "El correo ya está registrado", 409
    user = User(email=email_clean)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user, None, 201


def authenticate_user(email, password):
    if not email or not password:
        return None, None, None
    user = User.query.filter_by(email=(email or "").lower().strip()).first()
    if not user or not user.check_password(password):
        return None, None, None
    access = create_access_token(identity=str(user.id))
    refresh = create_refresh_token(identity=str(user.id))
    return user, access, refresh


def revoke_refresh_token(refresh_token):
    try:
        from flask_jwt_extended import decode_token
        payload = decode_token(refresh_token, allow_expired=False)
    except Exception:
        return False
    if payload.get("type") != "refresh":
        return False
    jti = payload.get("jti")
    identity = payload.get("sub")
    if not jti:
        return False
    existing = RevokedToken.query.filter_by(jti=jti).first()
    if existing:
        return True
    rv = RevokedToken(jti=jti,
                    user_id=int(identity) if identity else None,
                    reason="logout")
    db.session.add(rv)
    db.session.commit()
    return True
