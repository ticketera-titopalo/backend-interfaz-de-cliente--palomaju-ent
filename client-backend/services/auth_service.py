"""Servicio de autenticacion, emision y revocacion de tokens."""

import re

from flask_jwt_extended import create_access_token, create_refresh_token, decode_token
from extensions import db
from core.security import hash_password, verify_password
from models import User, RevokedToken


EMAIL_RE = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


def _is_valid_email(email):
    return bool(re.match(EMAIL_RE, email))


def _validate_credentials_format(email, password):
    if not isinstance(email, str) or not isinstance(password, str) or not email.strip() or not password:
        return None, "Email y contraseña son obligatorios"
    if len(password) < 8:
        return None, "La contraseña debe tener al menos 8 caracteres"
    email_clean = email.lower().strip()
    if not _is_valid_email(email_clean):
        return None, "Email inválido"
    return email_clean, None


def _validate_registration(email, password):
    """Devuelve (email_limpio, error, status)."""
    email_clean, err = _validate_credentials_format(email, password)
    if err:
        return None, err, 400
    if User.query.filter_by(email=email_clean).first():
        return None, "El correo ya está registrado", 409
    return email_clean, None, None


def register_user(email, password):
    email_clean, err, status = _validate_registration(email, password)
    if err:
        return None, err, status
    user = User(email=email_clean)
    user.password_hash = hash_password(password)
    db.session.add(user)
    db.session.commit()
    return user, None, 201


def authenticate_user(email, password):
    if not isinstance(email, str) or not isinstance(password, str) or not email.strip() or not password:
        return None, None, None
    user = User.query.filter_by(email=email.lower().strip()).first()
    if not user or not verify_password(password, user.password_hash):
        return None, None, None
    identity = str(user.id)
    return user, create_access_token(identity=identity), create_refresh_token(identity=identity)


def _decode_refresh(refresh_token):
    """Devuelve el payload si es un refresh token valido, o None."""
    if not isinstance(refresh_token, str) or not refresh_token.strip():
        return None
    try:
        payload = decode_token(refresh_token, allow_expired=False)
    except Exception:
        return None
    if payload.get("type") != "refresh" or not payload.get("jti"):
        return None
    return payload


def revoke_refresh_token(refresh_token):
    payload = _decode_refresh(refresh_token)
    if not payload:
        return False
    jti = payload.get("jti")
    if RevokedToken.query.filter_by(jti=jti).first():
        return True
    identity = payload.get("sub")
    rv = RevokedToken(
        jti=jti,
        user_id=int(identity) if identity else None,
        reason="logout",
    )
    db.session.add(rv)
    db.session.commit()
    return True