from flask import Blueprint, jsonify

from services.concert_service import list_concerts, get_concert

bp = Blueprint("concerts", __name__)


@bp.route("/api/concerts", methods=["GET"])
def concerts_list():
    concerts = list_concerts()
    return jsonify([{
        "id": c.id,
        "name": c.name,
        "description": c.description,
        "date": c.date,
        "price": c.price,
        "stock": c.stock,
        "image_url": c.image_url,
    } for c in concerts]), 200


@bp.route("/api/concerts/<int:concert_id>", methods=["GET"])
def concert_detail(concert_id):
    concert = get_concert(concert_id)
    if not concert:
        return jsonify({"message": "Concierto no encontrado"}), 404
    return jsonify({
        "id": concert.id,
        "name": concert.name,
        "description": concert.description,
        "date": concert.date,
        "price": concert.price,
        "stock": concert.stock,
        "image_url": concert.image_url,
    }), 200
