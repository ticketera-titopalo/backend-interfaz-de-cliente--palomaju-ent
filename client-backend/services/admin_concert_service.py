"""Servicio de administracion de conciertos (issue 12)."""

from extensions import db
from models import Concert, Purchase


def _err(msg, status=400):
    return {"message": msg}, status


def create_concert(data):
    data = data or {}
    name = (data.get("name") or "").strip()
    if not name:
        return None, _err("El nombre es obligatorio", 400)
    date = (data.get("date") or "").strip()
    if not date:
        return None, _err("La fecha es obligatoria", 400)
    try:
        price = float(data.get("price"))
    except (TypeError, ValueError):
        return None, _err("price debe ser un numero mayor a 0", 400)
    if price <= 0:
        return None, _err("price debe ser mayor a 0", 400)
    stock = data.get("stock", 0)
    try:
        stock = int(stock)
    except (TypeError, ValueError):
        return None, _err("stock debe ser un entero no negativo", 400)
    if stock < 0:
        return None, _err("stock no puede ser negativo", 400)
    try:
        concert = Concert(
            name=name,
            description=data.get("description"),
            date=date,
            price=price,
            stock=stock,
            image_url=data.get("image_url"),
        )
        db.session.add(concert)
        db.session.commit()
        return concert, None
    except Exception as exc:
        db.session.rollback()
        return None, ({"error": "Error interno del servidor"}, 500)


def update_concert(concert_id, data):
    concert = db.session.get(Concert, concert_id)
    if not concert:
        return None, _err("Concierto no encontrado", 404)
    data = data or {}
    if "name" in data:
        name = (data.get("name") or "").strip()
        if not name:
            return None, _err("name no puede estar vacio", 400)
        concert.name = name
    if "description" in data:
        concert.description = data.get("description")
    if "date" in data:
        d = (data.get("date") or "").strip()
        if not d:
            return None, _err("date no puede estar vacio", 400)
        concert.date = d
    if "price" in data:
        try:
            price = float(data.get("price"))
        except (TypeError, ValueError):
            return None, _err("price debe ser un numero", 400)
        if price <= 0:
            return None, _err("price debe ser mayor a 0", 400)
        concert.price = price
    if "stock" in data:
        try:
            stock = int(data.get("stock"))
        except (TypeError, ValueError):
            return None, _err("stock debe ser un entero", 400)
        if stock < 0:
            return None, _err("stock no puede ser negativo", 400)
        concert.stock = stock
    if "image_url" in data:
        concert.image_url = data.get("image_url")
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
    try:
        cantidad = int(cantidad)
    except (TypeError, ValueError):
        return None, 0, _err("cantidad debe ser un entero mayor a 0", 400)
    if cantidad <= 0:
        return None, 0, _err("cantidad debe ser mayor a 0", 400)
    concert.stock += cantidad
    db.session.commit()
    return concert, cantidad, None
