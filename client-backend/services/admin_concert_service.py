"""Servicio de administracion de conciertos (issue 12)."""

from extensions import db
from models import Concert, Purchase


def _err(msg, status=400):
    return {"message": msg}, status


def _parse_number(raw, cast, msgs):
    """cast=cast_fn, msgs=(error_cast, error_valor, minimo)."""
    if isinstance(raw, bool):
        return None, _err(msgs[0])
    try:
        value = cast(raw)
    except (TypeError, ValueError):
        return None, _err(msgs[0])
    if value <= msgs[2]:
        return None, _err(msgs[1])
    return value, None


def _clean_text(data, key):
    raw = data.get(key)
    return raw.strip() if isinstance(raw, str) else ""


def _validate_create(data):
    name = _clean_text(data, "name")
    if not name:
        return None, _err("El nombre es obligatorio")
    date = _clean_text(data, "date")
    if not date:
        return None, _err("La fecha es obligatoria")
    price, err = _parse_number(
        data.get("price"), float,
        ("price debe ser un numero mayor a 0", "price debe ser mayor a 0", 0),
    )
    if err:
        return None, err
    stock, err = _parse_number(
        data.get("stock", 0), int,
        ("stock debe ser un entero no negativo", "stock no puede ser negativo", -1),
    )
    if err:
        return None, err
    return {
        "name": name, "date": date, "price": price,
        "stock": stock, "description": data.get("description"),
        "image_url": data.get("image_url"),
    }, None


def create_concert(data):
    fields, err = _validate_create(data or {})
    if err:
        return None, err
    try:
        concert = Concert(**fields)
        db.session.add(concert)
        db.session.commit()
        return concert, None
    except Exception:
        db.session.rollback()
        return None, ({"error": "Error interno del servidor"}, 500)


def _update_required_str(concert, data, field):
    if field not in data:
        return None
    val = _clean_text(data, field)
    if not val:
        return _err(f"{field} no puede estar vacio")
    setattr(concert, field, val)
    return None


def _update_numeric(concert, data, field, cast, msgs):
    if field not in data:
        return None
    val, err = _parse_number(data.get(field), cast, msgs)
    if err:
        return err
    setattr(concert, field, val)
    return None


def _apply_updates(concert, data):
    """Devuelve None si todo es valido, o (err, status)."""
    for field in ("name", "date"):
        err = _update_required_str(concert, data, field)
        if err:
            return err
    for field in ("description", "image_url"):
        if field in data:
            setattr(concert, field, data.get(field))
    err = _update_numeric(
        concert, data, "price", float,
        ("price debe ser un numero", "price debe ser mayor a 0", 0),
    )
    if err:
        return err
    return _update_numeric(
        concert, data, "stock", int,
        ("stock debe ser un entero", "stock no puede ser negativo", -1),
    )


def update_concert(concert_id, data):
    concert = db.session.get(Concert, concert_id)
    if not concert:
        return None, _err("Concierto no encontrado", 404)
    err = _apply_updates(concert, data or {})
    if err:
        return None, err
    db.session.commit()
    return concert, None


def delete_concert(concert_id):
    concert = db.session.get(Concert, concert_id)
    if not concert:
        return False, _err("Concierto no encontrado", 404)
    if Purchase.query.filter_by(concert_id=concert_id).first():
        return False, _err("No se puede borrar: hay compras asociadas", 409)
    db.session.delete(concert)
    db.session.commit()
    return True, None


def restock(concert_id, cantidad):
    concert = db.session.get(Concert, concert_id)
    if not concert:
        return None, 0, _err("Concierto no encontrado", 404)
    cantidad, err = _parse_number(
        cantidad, int,
        ("cantidad debe ser un entero mayor a 0", "cantidad debe ser mayor a 0", 0),
    )
    if err:
        return None, 0, err
    concert.stock += cantidad
    db.session.commit()
    return concert, cantidad, None