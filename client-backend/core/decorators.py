from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from extensions import db
from models import User


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        current_user_id = int(get_jwt_identity())
        user = db.session.get(User, current_user_id)
        if not user or user.role != "admin":
            return jsonify({"message": "Se requieren permisos de administrador"}), 403
        return fn(*args, **kwargs)
    return wrapper
