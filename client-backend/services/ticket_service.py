"""Servicio de acceso a tickets e historial de compras."""

from extensions import db
from models import Ticket, Purchase, TicketRedemption


def list_user_purchases(user_id):
    return Purchase.query.filter_by(user_id=int(user_id)).order_by(
        Purchase.created_at.desc()).all()


def list_user_tickets(user_id):
    return Ticket.query.filter_by(user_id=int(user_id)).order_by(
        Ticket.created_at.desc()).all()


def tickets_for_purchase(purchase_id, user_id):
    purchase = db.session.get(Purchase, purchase_id)
    if not purchase:
        return None, "Compra no encontrada", 404
    if purchase.user_id != int(user_id):
        return None, "No tenés acceso a esta compra", 403
    tickets = Ticket.query.filter_by(purchase_id=purchase.id).order_by(
        Ticket.id.asc()).all()
    return tickets, None, 200


def _previous_redemption(ticket_id):
    return (TicketRedemption.query
            .filter_by(ticket_id=ticket_id)
            .order_by(TicketRedemption.redeemed_at.desc())
            .first())


def _build_success(ticket, redemption, admin_user_id):
    return {
        "message": "Entrada validada con éxito",
        "code": ticket.code,
        "used": True,
        "validated_at": redemption.redeemed_at.isoformat(),
        "validated_by": int(admin_user_id),
        "ticket_id": ticket.id,
        "purchase_id": ticket.purchase_id,
        "propietario": {"user_id": ticket.user_id, "email": ticket.user.email},
        "concierto": {
            "id": ticket.concert_id,
            "name": ticket.concert.name,
            "date": ticket.concert.date,
        },
    }


def _build_already_used(ticket, previous):
    return {
        "message": "Entrada ya utilizada",
        "code": ticket.code,
        "validated_at": previous.redeemed_at.isoformat() if previous else None,
        "validated_by": previous.admin_user_id if previous else None,
    }


def validate_ticket(code, admin_user_id):
    code = (code or "").strip()
    if not code:
        return {"message": "El código de la entrada es obligatorio"}, 400
    ticket = Ticket.query.filter_by(code=code).first()
    if not ticket:
        return {"message": "Entrada no encontrada"}, 404
    if ticket.used:
        return _build_already_used(ticket, _previous_redemption(ticket.id)), 409
    try:
        ticket.used = True
        redemption = TicketRedemption(ticket_id=ticket.id,
                                     admin_user_id=int(admin_user_id))
        db.session.add(redemption)
        db.session.commit()
        return _build_success(ticket, redemption, admin_user_id), 200
    except Exception:
        db.session.rollback()
        return {"error": "Error interno del servidor"}, 500
