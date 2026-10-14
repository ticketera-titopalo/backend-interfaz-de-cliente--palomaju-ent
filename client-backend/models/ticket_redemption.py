from datetime import datetime
from extensions import db


class TicketRedemption(db.Model):
    __tablename__ = "ticket_redemptions"

    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey("tickets.id"), nullable=False)
    admin_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    redeemed_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    ticket = db.relationship("Ticket", backref=db.backref("redemptions", lazy=True))
    admin = db.relationship("User", backref=db.backref("redemptions", lazy=True))
