from flask import Blueprint, jsonify, request

from flask_jwt_extended import jwt_required, get_jwt_identity
from core.decorators import admin_required
from services import admin_concert_service as svc

bp = Blueprint("admin_concerts", __name__)


@bp.route("/api/admin/concerts", methods=["POST"])
@jwt_required()
@admin_required
def create():
    concert, err = svc.create_concert(request.get_json(silent=True) or {})
    if err is not None:
        body, status = err
        return jsonify(body), status
    return jsonify(concert.to_dict()), 201


@bp.route("/api/admin/concerts/<int:concert_id>", methods=["PUT"])
@jwt_required()
@admin_required
def update(concert_id):
    concert, err = svc.update_concert(concert_id,
                                      request.get_json(silent=True) or {})
    if err is not None:
        body, status = err
        return jsonify(body), status
    return jsonify(concert.to_dict()), 200


@bp.route("/api/admin/concerts/<int:concert_id>", methods=["DELETE"])
@jwt_required()
@admin_required
def delete(concert_id):
    ok, err = svc.delete_concert(concert_id)
    if not ok:
        body, status = err
        return jsonify(body), status
    return "", 204


@bp.route("/api/admin/concerts/<int:concert_id>/stock", methods=["POST"])
@jwt_required()
@admin_required
def restock(concert_id):
    data = request.get_json(silent=True) or {}
    concert, cantidad, err = svc.restock(concert_id, data.get("cantidad"))
    if err is not None:
        body, status = err
        return jsonify(body), status
    return jsonify({"id": concert.id, "stock": concert.stock,
                   "agregado": cantidad}), 200
