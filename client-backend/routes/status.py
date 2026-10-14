from flask import Blueprint, jsonify
from extensions import db
from sqlalchemy import text

bp = Blueprint("status", __name__)


@bp.route("/api/status", methods=["GET"])
def status():
    db.session.execute(text("SELECT 1"))
    return jsonify({"status": "online", "database": "connected"}), 200
