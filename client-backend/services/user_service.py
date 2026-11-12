"""Servicio de perfil del usuario autenticado."""

from extensions import db
from models import User


FORBIDDEN_FIELDS = {"email", "password", "role", "password_hash", "id"}
SIMPLE_FIELDS = (("nombre", 80), ("apellido", 80), ("telefono", 30))


def _clean(value, max_len):
    """Devuelve (valor_limpio, error_msg)."""
    if value is None:
        return None, None
    v = str(value).strip()
    if len(v) > max_len:
        return None, f"no puede superar {max_len} caracteres"
    return (v if v != "" else None), None


def get_current_user(user_id):
    return db.session.get(User, int(user_id))


def _has_editable_value(data, field):
    return field in data and data.get(field) is not None


def _apply_simple(user, data, field, max_len):
    if not _has_editable_value(data, field):
        return None
    v, err = _clean(data.get(field), max_len)
    if err:
        return f"{field} {err}"
    setattr(user, field, v)
    return None


def _is_dni_taken(user_id, dni):
    if dni is None:
        return False
    existing = User.query.filter_by(dni=dni).first()
    return bool(existing and existing.id != user_id)


def _apply_dni(user, data):
    if not _has_editable_value(data, "dni"):
        return None
    v, err = _clean(data.get("dni"), 20)
    if err:
        return f"dni {err}"
    if _is_dni_taken(user.id, v):
        return "DNI ya registrado"
    user.dni = v
    return None


def _apply_all_fields(user, data):
    for field, max_len in SIMPLE_FIELDS:
        msg = _apply_simple(user, data, field, max_len)
        if msg:
            return msg, 400
    msg = _apply_dni(user, data)
    if msg:
        return msg, (409 if msg == "DNI ya registrado" else 400)
    return None, 200


def update_profile(user_id, data):
    user = db.session.get(User, int(user_id))
    if not user:
        return None, "Usuario no encontrado", 404
    payload = data or {}
    if any(f in payload for f in FORBIDDEN_FIELDS):
        return None, "Campos no editables por esta vía", 400

    msg, status = _apply_all_fields(user, payload)
    if msg:
        return None, msg, status

    db.session.commit()
    return user, None, 200