import os
from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv
from sqlalchemy import text # Para el health check
from datetime import datetime # Para manejar fechas si decides usar DateTime
import uuid 
from werkzeug.security import generate_password_hash, check_password_hash

# Cargar variables de entorno
load_dotenv(dotenv_path="../.env")

print("--- INICIANDO CONFIGURACIÓN DEL SERVIDOR ---")

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "clave_secreta_por_defecto")
jwt = JWTManager(app)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}})

# Configuración DB
user = os.getenv('MYSQL_USER')
password = os.getenv('MYSQL_PASSWORD')
db_name = os.getenv('MYSQL_DATABASE')
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{user}:{password}@localhost:3306/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- MODELOS DE DATOS ---

class Concert(db.Model):
    __tablename__ = 'concerts'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    date = db.Column(db.String(50), nullable=False) # Usamos String para simplificar la entrega inicial
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.String(255), nullable=True)


# NUEVO MODELO USER (ISSUE 5)
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='client', nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "role": self.role
        }


# --- REGISTRO DE COMPRAS ---
class Purchase(db.Model):
    """Historial de compras: qué compró cada usuario y a qué hora."""
    __tablename__ = 'purchases'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    concert_id = db.Column(db.Integer, db.ForeignKey('concerts.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('purchases', lazy=True))
    concert = db.relationship('Concert', backref=db.backref('purchases', lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "concert_id": self.concert_id,
            "concierto": self.concert.name if self.concert else None,
            "fecha": self.concert.date if self.concert else None,
            "quantity": self.quantity,
            "total_price": float(self.total_price),
            "created_at": self.created_at.isoformat()
        }


# --- ENTRADAS / TICKETS POR COMPRA (ISSUE 7) ---
class Ticket(db.Model):
    """Una entrada individual. Cada unidad comprada genera un ticket."""
    __tablename__ = 'tickets'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False)
    purchase_id = db.Column(db.Integer, db.ForeignKey('purchases.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    concert_id = db.Column(db.Integer, db.ForeignKey('concerts.id'), nullable=False)
    used = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    purchase = db.relationship('Purchase', backref=db.backref('tickets', lazy=True))
    user = db.relationship('User', backref=db.backref('tickets', lazy=True))
    concert = db.relationship('Concert', backref=db.backref('tickets', lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "code": self.code,
            "purchase_id": self.purchase_id,
            "concert_id": self.concert_id,
            "concierto": self.concert.name if self.concert else None,
            "fecha": self.concert.date if self.concert else None,
            "used": self.used,
            "created_at": self.created_at.isoformat()
        }


def generar_codigo_ticket():
    """Genera un código único con formato TKT-XXXXXX."""
    while True:
        codigo = f"TKT-{uuid.uuid4().hex[:6].upper()}"
        if not Ticket.query.filter_by(code=codigo).first():
            return codigo


# --- CREACIÓN DE TABLAS Y SEED DE DATOS ---
with app.app_context():
    db.create_all() # Crea la tabla concerts y users si no existen
    
    # Verificamos si ya hay conciertos para no duplicarlos cada vez que reinicies
    if Concert.query.count() == 0:
        test_concerts = [
            Concert(name="Duki - ADA Tour", description="El trap argentino llega al estadio.", date="2024-12-10", price=45000.0, stock=100, image_url="https://via.placeholder.com/150"),
            Concert(name="Wos - Descartable", description="Presentación del nuevo disco.", date="2024-11-15", price=35000.0, stock=50, image_url="https://via.placeholder.com/150"),
            Concert(name="Babasónicos", description="Show íntimo en el Luna Park.", date="2024-10-20", price=28000.0, stock=20, image_url="https://via.placeholder.com/150")
        ]
        db.session.bulk_save_objects(test_concerts)
        db.session.commit()
        print("Base de datos inicializada con conciertos de prueba.")


# --- ENDPOINTS ---

@app.route('/api/status', methods=['GET'])
def get_status():
    db.session.execute(text('SELECT 1'))
    return jsonify({"status": "online", "database": "connected"}), 200


@app.route('/api/concerts', methods=['GET'])
def get_concerts():
    try:
        concerts = Concert.query.all()
        return jsonify([{
            "id": c.id,
            "name": c.name,
            "description": c.description,
            "date": c.date,
            "price": c.price,
            "stock": c.stock,
            "image_url": c.image_url
        } for c in concerts]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --- NUEVOS ENDPOINTS DE AUTENTICACIÓN (ISSUE 5) ---

@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json() or {}
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({"message": "Email y contraseña son obligatorios"}), 400

        # Verificar si el usuario ya existe
        if User.query.filter_by(email=email).first():
            return jsonify({"message": "El correo ya está registrado"}), 400

        # Crear nuevo usuario con contraseña encriptada
        new_user = User(email=email)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        return jsonify({
            "message": "Usuario registrado exitosamente",
            "user": new_user.to_dict()
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json() or {}
        email = data.get('email')
        password = data.get('password')

        user = User.query.filter_by(email=email).first()

        # Validar existencia de usuario y contraseña
        if not user or not user.check_password(password):
            return jsonify({"message": "Credenciales inválidas"}), 401

        # Crear token de acceso con la ID del usuario como string
        access_token = create_access_token(identity=str(user.id))

        return jsonify({
            "access_token": access_token,
            "user": user.to_dict()
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ENDPOINT DE COMPRA PROTEGIDO CON JWT
@app.route('/api/purchase', methods=['POST'])
@jwt_required()
def purchase_ticket():
    data = request.get_json(silent=True) or {}
    current_user_id = int(get_jwt_identity())

    # 1. Validar que el usuario del token exista
    user = db.session.get(User, current_user_id)
    if not user:
        return jsonify({"message": "Usuario del token no encontrado"}), 401

    concert_id = data.get('concert_id')
    quantity = data.get('quantity', 1)

    # 2. Validar el payload: concert_id debe ser un entero
    try:
        concert_id = int(concert_id)
    except (TypeError, ValueError):
        return jsonify({"message": "concert_id debe ser un número"}), 400

    # 3. Validar que la cantidad sea un entero positivo
    if not isinstance(quantity, int) or isinstance(quantity, bool) or quantity < 1:
        return jsonify({"message": "La cantidad debe ser un entero mayor a 0"}), 400

    # 4. Buscar el concierto
    concert = db.session.get(Concert, concert_id)
    if not concert:
        return jsonify({"message": "Concierto no encontrado"}), 404

    # 5. VALIDACIÓN DE STOCK: ¿alcanza para lo que pide el cliente?
    if concert.stock < quantity:
        return jsonify({
            "message": "Stock insuficiente",
            "stock_disponible": concert.stock,
            "solicitado": quantity
        }), 400

    try:
        # 6. Descontar stock
        concert.stock -= quantity

        # 7. Registrar la compra
        purchase = Purchase(
            user_id=user.id,
            concert_id=concert.id,
            quantity=quantity,
            total_price=round(concert.price * quantity, 2)
        )
        db.session.add(purchase)
        db.session.flush()  # Necesario para obtener purchase.id antes de crear los tickets

        # 8. Generar un ticket por cada unidad comprada
        for _ in range(quantity):
            ticket = Ticket(
                code=generar_codigo_ticket(),
                purchase_id=purchase.id,
                user_id=user.id,
                concert_id=concert.id
            )
            db.session.add(ticket)

        db.session.commit()
        return jsonify({
            "message": "Compra realizada con éxito",
            "user_id": user.id,
            "concierto": concert.name,
            "quantity": quantity,
            "total_price": float(purchase.total_price),
            "nuevo_stock": concert.stock,
            "purchase_id": purchase.id,
            "tickets_created": quantity
        }), 201

    except Exception as e:
        db.session.rollback()  # Si algo falla, no queda el stock a medias
        return jsonify({"error": str(e)}), 500


# Historial de compras del usuario autenticado
@app.route('/api/user/purchases', methods=['GET'])
@jwt_required()
def get_purchases():
    current_user_id = int(get_jwt_identity())

    purchases = Purchase.query.filter_by(user_id=current_user_id) \
                               .order_by(Purchase.created_at.desc()).all()

    return jsonify([p.to_dict() for p in purchases]), 200


# Entradas del usuario autenticado
@app.route('/api/user/tickets', methods=['GET'])
@jwt_required()
def get_tickets():
    current_user_id = int(get_jwt_identity())

    tickets = Ticket.query.filter_by(user_id=current_user_id) \
                          .order_by(Ticket.created_at.desc()).all()

    return jsonify([t.to_dict() for t in tickets]), 200


# Entradas de una compra puntual (solo si es del usuario autenticado)
@app.route('/api/user/purchases/<int:purchase_id>/tickets', methods=['GET'])
@jwt_required()
def get_purchase_tickets(purchase_id):
    current_user_id = int(get_jwt_identity())

    purchase = db.session.get(Purchase, purchase_id)

    if not purchase:
        return jsonify({"message": "Compra no encontrada"}), 404

    if purchase.user_id != current_user_id:
        return jsonify({"message": "No tenés acceso a esta compra"}), 403

    tickets = Ticket.query.filter_by(purchase_id=purchase.id) \
                          .order_by(Ticket.id.asc()).all()

    return jsonify([t.to_dict() for t in tickets]), 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)