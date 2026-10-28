from errors import error
from flask import Blueprint, jsonify, request

from services.concert_service import (
    list_concerts,
    get_concert,
    search_concerts,
    is_valid_date,
    ALLOWED_ORDERS,
)

bp = Blueprint("concerts", __name__)


@bp.route("/api/concerts", methods=["GET"])
def concerts_list():
    q = (request.args.get("q") or "").strip() or None
    fecha_desde = request.args.get("fecha_desde") or None
    fecha_hasta = request.args.get("fecha_hasta") or None
    order = (request.args.get("order") or "fecha_asc").strip()
    page_raw = request.args.get("page", "1")
    limit_raw = request.args.get("limit", "12")
    try:
        page = int(page_raw)
    except (ValueError, TypeError):
        page = None
    try:
        limit = int(limit_raw)
    except (ValueError, TypeError):
        limit = None

    if page is None or page < 1:
        return error("page debe ser entero >= 1", 400)
    if limit is None or limit < 1 or limit > 100:
        return error("limit debe ser entre 1 y 100", 400)
    if order not in ALLOWED_ORDERS:
        return error("order inválido", 400)
    if not is_valid_date(fecha_desde):
        return error("fecha_desde invalida", 400)
    if not is_valid_date(fecha_hasta):
        return error("fecha_hasta invalida", 400)

    concerts, total, page, limit, total_pages = search_concerts(
        q=q, fecha_desde=fecha_desde, fecha_hasta=fecha_hasta,
        order=order, page=page, limit=limit,
    )
    return jsonify({
        "concerts": [c.to_dict() for c in concerts],
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
    }), 200


@bp.route("/api/concerts/<int:concert_id>", methods=["GET"])
def concert_detail(concert_id):
    concert = get_concert(concert_id)
    if not concert:
        return error("Concierto no encontrado", 404)
    return jsonify(concert.to_dict()), 200
