"""Servicio de compra y emision de entradas."""

from extensions import db
from models import User, Concert, Purchase, Ticket
from models.ticket import generar_codigo_ticket


def _fail(msg, status=400, extra=None):
    body = {"message": msg}
    if extra:
        body.update(extra)
    return body, status


def buy(concert_id, quantity, user_id):
    # Validar payload
    try:
        pk = int(concert_id)
    except (TypeError, ValueError):
        return None, _fail("concert_id debe ser un número", 400)
    if not isinstance(quantity, int) or isinstance(quantity, bool) or quantity < 1:
        return None, _fail("La cantidad debe ser un entero mayor a 0", 400)

    # Verificar usuario
    user = db.session.get(User, int(user_id))
    if not user:
        return None, _fail("Usuario del token no encontrado", 401)

    # Verificar concierto
    concert = db.session.get(Concert, pk)
    if not concert:
        return None, _fail("Concierto no encontrado", 404)
    if concert.stock < quantity:
        return None, _fail("Stock insuficiente", 400, {
            "stock_disponible": concert.stock,
            "solicitado": quantity,
        })

    # Transaccion atomica
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
        for _ in range(quantity):
            db.session.add(Ticket(
                code=generar_codigo_ticket(),
                purchase_id=purchase.id,
                user_id=user.id,
                concert_id=concert.id,
            ))
        db.session.commit()
        data = {
            "message": "Compra realizada con éxito",
            "user_id": user.id,
            "concierto": concert.name,
            "quantity": quantity,
            "total_price": float(purchase.total_price),
            "nuevo_stock": concert.stock,
            "purchase_id": purchase.id,
            "tickets_created": quantity,
        }
        return data, None
    except Exception as exc:
        db.session.rollback()
        return None, {"error": "Error interno del servidor"}, 500
