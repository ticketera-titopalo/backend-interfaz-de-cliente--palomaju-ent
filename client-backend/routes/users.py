from flask import Blueprint, jsonify, request

from flask_jwt_extended import jwt_required, get_jwt_identity

from services.user_service import get_current_user, update_profile

bp = Blueprint("users", __name__)


@bp.route("/api/user/me", methods=["GET"])
@jwt_required()
def me():
    user = get_current_user(int(get_jwt_identity()))
    if not user:
        return jsonify({"message": "Usuario no encontrado"}), 404
    return jsonify(user.to_profile()), 200


@bp.route("/api/user/me", methods=["PUT"])
@jwt_required()
def update_me():
    current_user_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}
    user, msg, status = update_profile(current_user_id, data)
    if msg is not None:
        return jsonify({"message": msg}), status
    return jsonify(user.to_profile()), 200
