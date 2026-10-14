"""Blueprints (presentation layer)."""

from . import status, concerts, auth, purchase, tickets, admin


def register_blueprints(app):
    app.register_blueprint(status.bp)
    app.register_blueprint(concerts.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(purchase.bp)
    app.register_blueprint(tickets.bp)
    app.register_blueprint(admin.bp)
