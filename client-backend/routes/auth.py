from flask import Blueprint, jsonify, request, make_response
from flask_jwt_extended import (
    jwt_required, create_access_token, create_refresh_token,
    get_jwt_identity, decode_token,
)

from services.auth_service import register_user, authenticate_user, revoke_refresh_token

bp = Blueprint("auth", __name__)


@bp.route("/api/auth/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    user, msg, status = register_user(data.get("email"), data.get("password"))
    if msg is not None:
        return jsonify({"message": msg}), status
    return jsonify({"message": "Usuario registrado exitosamente",
                    "user": user.to_dict()}), status


@bp.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    user, access, refresh = authenticate_user(data.get("email"), data.get("password"))
    if user is None:
        return jsonify({"message": "Credenciales inválidas"}), 401
    return jsonify({
        "access_token": access,
        "refresh_token": refresh,
        "user": user.to_dict(),
    }), 200


@bp.route("/api/auth/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    new_access = create_access_token(identity=identity)
    return jsonify({"access_token": new_access}), 200


@bp.route("/api/auth/logout", methods=["POST"])
@jwt_required()
def logout():
    data = request.get_json(silent=True) or {}
    revoke_refresh_token(data.get("refresh_token"))
    return jsonify({"message": "Sesión cerrada"}), 200
