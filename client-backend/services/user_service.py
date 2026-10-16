"""Servicio de perfil del usuario autenticado."""

from extensions import db
from models import User


FORBIDDEN_FIELDS = {"email", "password", "role", "password_hash", "id"}


def get_current_user(user_id):
    return db.session.get(User, int(user_id))


def update_profile(user_id, data):
    user = db.session.get(User, int(user_id))
    if not user:
        return user, "Usuario no encontrado", 404

    # Campos no editables por esta via
    if any(f in (data or {}) for f in FORBIDDEN_FIELDS):
        return None, "Campos no editables por esta vía", 400

    data = data or {}
    # nombre
    if "nombre" in data and data.get("nombre") is not None:
        v = str(data.get("nombre")).strip()
        if len(v) > 80:
            return None, "nombre no puede superar 80 caracteres", 400
        user.nombre = v if v != "" else None
    # apellido
    if "apellido" in data and data.get("apellido") is not None:
        v = str(data.get("apellido")).strip()
        if len(v) > 80:
            return None, "apellido no puede superar 80 caracteres", 400
        user.apellido = v if v != "" else None
    # telefono
    if "telefono" in data and data.get("telefono") is not None:
        v = str(data.get("telefono")).strip()
        if len(v) > 30:
            return None, "telefono no puede superar 30 caracteres", 400
        user.telefono = v if v != "" else None
    # dni
    if "dni" in data and data.get("dni") is not None:
        v = str(data.get("dni")).strip()
        if len(v) > 20:
            return None, "dni no puede superar 20 caracteres", 400
        existing = User.query.filter_by(dni=v).first()
        if existing and existing.id != user.id:
            return None, "DNI ya registrado", 409
        user.dni = v if v != "" else None

    db.session.commit()
    return user, None, 200
