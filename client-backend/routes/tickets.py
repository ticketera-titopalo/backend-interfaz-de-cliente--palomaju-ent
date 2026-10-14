from flask import Blueprint, jsonify

from flask_jwt_extended import jwt_required, get_jwt_identity

from services.ticket_service import (
    list_user_purchases,
    list_user_tickets,
    tickets_for_purchase,
)

bp = Blueprint("tickets", __name__)


@bp.route("/api/user/purchases", methods=["GET"])
@jwt_required()
def user_purchases():
    current_user_id = int(get_jwt_identity())
    purchases = list_user_purchases(current_user_id)
    return jsonify([p.to_dict() for p in purchases]), 200


@bp.route("/api/user/tickets", methods=["GET"])
@jwt_required()
def user_tickets():
    current_user_id = int(get_jwt_identity())
    tickets = list_user_tickets(current_user_id)
    return jsonify([t.to_dict() for t in tickets]), 200


@bp.route("/api/user/purchases/<int:purchase_id>/tickets", methods=["GET"])
@jwt_required()
def purchase_tickets(purchase_id):
    current_user_id = int(get_jwt_identity())
    tickets, msg, status = tickets_for_purchase(purchase_id, current_user_id)
    if tickets is None:
        return jsonify({"message": msg}), status
    return jsonify([t.to_dict() for t in tickets]), 200
