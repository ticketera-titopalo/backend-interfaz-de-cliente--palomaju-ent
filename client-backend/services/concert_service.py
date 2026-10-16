"""Servicio de acceso, busqueda y paginacion de conciertos."""

from datetime import datetime

from extensions import db
from models import Concert


ALLOWED_ORDERS = {
    "fecha_asc": Concert.date.asc(),
    "fecha_desc": Concert.date.desc(),
    "precio_asc": Concert.price.asc(),
    "precio_desc": Concert.price.desc(),
}


def list_concerts():
    return Concert.query.order_by(Concert.id.asc()).all()


def get_concert(concert_id):
    try:
        pk = int(concert_id)
    except (TypeError, ValueError):
        return None
    return db.session.get(Concert, pk)


def is_valid_date(value):
    if not value:
        return True
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return True
    except (ValueError, TypeError):
        return False


def search_concerts(q=None, fecha_desde=None, fecha_hasta=None,
                    order="fecha_asc", page=1, limit=12):
    query = Concert.query
    if q:
        pattern = f"%{q}%"
        query = query.filter(
            db.or_(Concert.name.ilike(pattern),
                   Concert.description.ilike(pattern)))
    if fecha_desde:
        query = query.filter(Concert.date >= fecha_desde)
    if fecha_hasta:
        query = query.filter(Concert.date <= fecha_hasta)

    total = query.count()

    order_clause = ALLOWED_ORDERS.get(order)
    if order_clause is not None:
        query = query.order_by(order_clause)
    else:
        query = query.order_by(Concert.id.asc())

    page = max(1, int(page))
    limit = max(1, min(int(limit), 100))
    concerts = query.offset((page - 1) * limit).limit(limit).all()
    total_pages = (total + limit - 1) // limit if total else 0
    return concerts, total, page, limit, total_pages
