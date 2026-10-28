from flask import jsonify


def error(msg, status=400):
    """Respuesta de error estandar de negocio: {"message": ...}."""
    return jsonify({"message": msg}), status


def register_error_handlers(app):
    """Handlers globales para no filtrar detalles internos al cliente."""

    @app.errorhandler(404)
    def not_found(_err):
        return jsonify({"message": "Recurso no encontrado"}), 404

    @app.errorhandler(405)
    def method_not_allowed(_err):
        return jsonify({"message": "Método no permitido"}), 405

    @app.errorhandler(400)
    def bad_request(err):
        desc = getattr(err, "description", None)
        if isinstance(desc, str) and desc and desc != "Bad Request":
            return jsonify({"message": desc}), 400
        return jsonify({"message": "Solicitud inválida"}), 400

    @app.errorhandler(500)
    def internal_error(err):
        app.logger.exception("Error interno no manejado")
        return jsonify({"error": "Error interno del servidor"}), 500

    @app.errorhandler(Exception)
    def unhandled_exception(err):
        app.logger.exception("Excepción no manejada")
        return jsonify({"error": "Error interno del servidor"}), 500
