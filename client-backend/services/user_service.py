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


def _check_forbidden(data):
    return any(f in (data or {}) for f in FORBIDDEN_FIELDS)


def _apply_simple(user, data, field, max_len):
    if field not in data or data.get(field) is None:
        return None
    v, err = _clean(data.get(field), max_len)
    if err:
        return f"{field} {err}"
    setattr(user, field, v)
    return None


def _apply_dni(user, data):
    if "dni" not in data or data.get("dni") is None:
        return None
    v, err = _clean(data.get("dni"), 20)
    if err:
        return f"dni {err}"
    if v is not None:
        existing = User.query.filter_by(dni=v).first()
        if existing and existing.id != user.id:
            return "DNI ya registrado"
    user.dni = v
    return None


def update_profile(user_id, data):
    user = db.session.get(User, int(user_id))
    if not user:
        return None, "Usuario no encontrado", 404
    data = data or {}
    if _check_forbidden(data):
        return None, "Campos no editables por esta vía", 400

    for field, max_len in SIMPLE_FIELDS:
        msg = _apply_simple(user, data, field, max_len)
        if msg:
            return None, msg, 400
    msg = _apply_dni(user, data)
    if msg:
        status = 409 if msg == "DNI ya registrado" else 400
        return None, msg, status

    db.session.commit()
    return user, None, 200
