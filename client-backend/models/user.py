from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="client", nullable=False)

    # Perfil extendido (ISSUE #11)
    nombre = db.Column(db.String(80), nullable=True)
    apellido = db.Column(db.String(80), nullable=True)
    dni = db.Column(db.String(20), unique=True, nullable=True)
    telefono = db.Column(db.String(30), nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def update_profile(self, **fields):
        """Actualiza solo los campos permitidos del perfil."""
        for field in ("nombre", "apellido", "dni", "telefono"):
            if field in fields and fields[field] is not None:
                setattr(self, field, fields[field])

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "role": self.role,
            "nombre": self.nombre,
            "apellido": self.apellido,
            "dni": self.dni,
            "telefono": self.telefono,
        }

    def to_profile(self):
        """Perfil público: sin password_hash."""
        return {
            "id": self.id,
            "email": self.email,
            "role": self.role,
            "nombre": self.nombre,
            "apellido": self.apellido,
            "dni": self.dni,
            "telefono": self.telefono,
        }
