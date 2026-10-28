"""Servicio de compra y emision de entradas."""

from extensions import db
from models import User, Concert, Purchase, Ticket
from models.ticket import generar_codigo_ticket


def _fail(msg, status=400, extra=None):
    body = {"message": msg}
    if extra:
        body.update(extra)
    return body, status


def _parse_payload(concert_id, quantity):
    """Devuelve (concert_id_int, error)."""
    try:
        pk = int(concert_id)
    except (TypeError, ValueError):
        return None, _fail("concert_id debe ser un número", 400)
    if not isinstance(quantity, int) or isinstance(quantity, bool) or quantity < 1:
        return None, _fail("La cantidad debe ser un entero mayor a 0", 400)
    return pk, None


def _check_stock(concert, quantity):
    if concert.stock < quantity:
        return _fail("Stock insuficiente", 400, {
            "stock_disponible": concert.stock,
            "solicitado": quantity,
        })
    return None


def _emitir_tickets(purchase, user_id, concert_id, quantity):
    for _ in range(quantity):
        db.session.add(Ticket(
            code=generar_codigo_ticket(),
            purchase_id=purchase.id,
            user_id=user_id,
            concert_id=concert_id,
        ))


def _build_purchase_response(user, concert, purchase, quantity):
    return {
        "message": "Compra realizada con éxito",
        "user_id": user.id,
        "concierto": concert.name,
        "quantity": quantity,
        "total_price": float(purchase.total_price),
        "nuevo_stock": concert.stock,
        "purchase_id": purchase.id,
        "tickets_created": quantity,
    }


def buy(concert_id, quantity, user_id):
    pk, err = _parse_payload(concert_id, quantity)
    if err:
        return None, err

    user = db.session.get(User, int(user_id))
    if not user:
        return None, _fail("Usuario del token no encontrado", 401)
    concert = db.session.get(Concert, pk)
    if not concert:
        return None, _fail("Concierto no encontrado", 404)
    err = _check_stock(concert, quantity)
    if err:
        return None, err

    try:
        concert.stock -= quantity
        purchase = Purchase(
            user_id=user.id,
            concert_id=concert.id,
            quantity=quantity,
            total_price=round(concert.price * quantity, 2),
        )
        db.session.add(purchase)
        db.session.flush()
        _emitir_tickets(purchase, user.id, concert.id, quantity)
        db.session.commit()
        return _build_purchase_response(user, concert, purchase, quantity), None
    except Exception:
        db.session.rollback()
        return None, {"error": "Error interno del servidor"}, 500
