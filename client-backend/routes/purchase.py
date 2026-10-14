from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from services.purchase_service import buy

bp = Blueprint("purchase", __name__)


@bp.route("/api/purchase", methods=["POST"])
@jwt_required()
def purchase():
    data = request.get_json(silent=True) or {}
    current_user_id = int(get_jwt_identity())
    data, error = buy(data.get("concert_id"), data.get("quantity", 1), current_user_id)
    if error is not None:
        body, status = error
        return jsonify(body), status
    return jsonify(data), 201
