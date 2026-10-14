from datetime import datetime
from extensions import db


class Purchase(db.Model):
    __tablename__ = "purchases"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    concert_id = db.Column(db.Integer, db.ForeignKey("concerts.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("purchases", lazy=True))
    concert = db.relationship("Concert", backref=db.backref("purchases", lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "concert_id": self.concert_id,
            "concierto": self.concert.name if self.concert else None,
            "fecha": self.concert.date if self.concert else None,
            "quantity": self.quantity,
            "total_price": float(self.total_price),
            "created_at": self.created_at.isoformat(),
        }
