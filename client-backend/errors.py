from flask import jsonify


def error(msg, status=400):
    """Respuesta de error estandar."""
    return jsonify({"message": msg}), status
