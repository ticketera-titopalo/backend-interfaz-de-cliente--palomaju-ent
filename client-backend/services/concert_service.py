"""Servicio de acceso a conciertos."""

from extensions import db
from models import Concert


def list_concerts():
    return Concert.query.order_by(Concert.id.asc()).all()


def get_concert(concert_id):
    try:
        pk = int(concert_id)
    except (TypeError, ValueError):
        return None
    return db.session.get(Concert, pk)
