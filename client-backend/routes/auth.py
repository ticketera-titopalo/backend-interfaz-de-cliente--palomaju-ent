from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity

from services.auth_service import register_user, authenticate_user
from models import User

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
    user, token = authenticate_user(data.get("email"), data.get("password"))
    if user is None:
        return jsonify({"message": "Credenciales inválidas"}), 401
    return jsonify({"access_token": token, "user": user.to_dict()}), 200
