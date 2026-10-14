import uuid
from datetime import datetime

from extensions import db

def generar_codigo_ticket():
    """Genera un código único con formato TKT-XXXXXX."""
    while True:
        codigo = f"TKT-{uuid.uuid4().hex[:6].upper()}"
        if not Ticket.query.filter_by(code=codigo).first():
            return codigo


class Ticket(db.Model):
    __tablename__ = "tickets"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False)
    purchase_id = db.Column(db.Integer, db.ForeignKey("purchases.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    concert_id = db.Column(db.Integer, db.ForeignKey("concerts.id"), nullable=False)
    used = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    purchase = db.relationship("Purchase", backref=db.backref("tickets", lazy=True))
    user = db.relationship("User", backref=db.backref("tickets", lazy=True))
    concert = db.relationship("Concert", backref=db.backref("tickets", lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "code": self.code,
            "purchase_id": self.purchase_id,
            "concert_id": self.concert_id,
            "concierto": self.concert.name if self.concert else None,
            "fecha": self.concert.date if self.concert else None,
            "used": self.used,
            "created_at": self.created_at.isoformat(),
        }
