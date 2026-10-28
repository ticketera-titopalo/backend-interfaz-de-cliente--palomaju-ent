from errors import error
from flask import Blueprint, jsonify, request

from services.concert_service import (
    get_concert,
    search_concerts,
    is_valid_date,
    ALLOWED_ORDERS,
)

bp = Blueprint("concerts", __name__)

DEFAULT_PAGE = "1"
DEFAULT_LIMIT = "12"


def _parse_int(raw, default=None):
    try:
        return int(raw)
    except (ValueError, TypeError):
        return default


def _validate_dates(fecha_desde, fecha_hasta):
    if not is_valid_date(fecha_desde):
        return error("fecha_desde invalida", 400)
    if not is_valid_date(fecha_hasta):
        return error("fecha_hasta invalida", 400)
    return None


def _validate_pagination(page, limit):
    if page is None or page < 1:
        return error("page debe ser entero >= 1", 400)
    if limit is None or limit < 1 or limit > 100:
        return error("limit debe ser entre 1 y 100", 400)
    return None


def _collect_params():
    """Devuelve (params, error_response)."""
    q = (request.args.get("q") or "").strip() or None
    fecha_desde = request.args.get("fecha_desde") or None
    fecha_hasta = request.args.get("fecha_hasta") or None
    order = (request.args.get("order") or "fecha_asc").strip()
    page = _parse_int(request.args.get("page", DEFAULT_PAGE))
    limit = _parse_int(request.args.get("limit", DEFAULT_LIMIT))

    if order not in ALLOWED_ORDERS:
        return None, error("order inválido", 400)
    err = _validate_dates(fecha_desde, fecha_hasta) or \
        _validate_pagination(page, limit)
    if err:
        return None, err

    return {
        "q": q, "fecha_desde": fecha_desde, "fecha_hasta": fecha_hasta,
        "order": order, "page": page, "limit": limit,
    }, None


@bp.route("/api/concerts", methods=["GET"])
def concerts_list():
    params, err = _collect_params()
    if err is not None:
        return err
    concerts, total, page, limit, total_pages = search_concerts(**params)
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
