from flask import Blueprint, jsonify

from extensions import db
from sqlalchemy import text

bp = Blueprint("status", __name__)

APP_VERSION = "1.0.0"


@bp.route("/api/status", methods=["GET"])
def status():
    try:
        db.session.execute(text("SELECT 1"))
        return jsonify({
            "status": "online",
            "database": "connected",
            "version": APP_VERSION,
        }), 200
    except Exception:
        return jsonify({"status": "online", "database": "disconnected"}), 500
