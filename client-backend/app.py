import os
from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv
from sqlalchemy import text # Para el health check
from datetime import datetime # Para manejar fechas si decides usar DateTime
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
    try:
        # Obtener la identidad del usuario desde el token JWT
        current_user_id = get_jwt_identity()
        
        return jsonify({
            "message": "Compra realizada con éxito",
            "user_id": current_user_id
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)