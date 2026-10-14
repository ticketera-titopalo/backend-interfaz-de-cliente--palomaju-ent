from flask import Blueprint, jsonify, request

from flask_jwt_extended import jwt_required, get_jwt_identity
from core.decorators import admin_required
from services.ticket_service import validate_ticket

bp = Blueprint("admin", __name__)


@bp.route("/api/admin/tickets/validate", methods=["POST"])
@jwt_required()
@admin_required
def validate():
    data = request.get_json(silent=True) or {}
    body, status = validate_ticket(data.get("code"), int(get_jwt_identity()))
    return jsonify(body), status
