import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv
from sqlalchemy import text # Para el health check
from datetime import datetime # Para manejar fechas si decides usar DateTime

# Cargar variables de entorno
load_dotenv(dotenv_path="../.env")

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}})

# Configuración DB
user = os.getenv('MYSQL_USER')
password = os.getenv('MYSQL_PASSWORD')
db_name = os.getenv('MYSQL_DATABASE')
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{user}:{password}@localhost:3306/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- TAREA 1: MODELO DE DATOS ---
class Concert(db.Model):
    __tablename__ = 'concerts'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    date = db.Column(db.String(50), nullable=False) # Usamos String para simplificar la entrega inicial
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.String(255), nullable=True)

# --- TAREA 2 y 3: CREACIÓN DE TABLAS Y SEED DE DATOS ---
with app.app_context():
    db.create_all() # Crea la tabla si no existe
    
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

# --- ENDPOINT DE STATUS (Existente) ---
@app.route('/api/status', methods=['GET'])
def get_status():
    try:
        db.session.execute(text('SELECT 1'))
        return jsonify({"status": "online", "database": "connected"}), 200
    except Exception as e:
        return jsonify({"status": "online", "database": "disconnected", "error": str(e)}), 500

# --- TAREA 4: ENDPOINT API PARA LISTAR CONCIERTOS ---
@app.route('/api/concerts', methods=['GET'])
def get_concerts():
    try:
        concerts = Concert.query.all()
        # Convertimos los objetos de la DB a una lista de diccionarios (JSON)
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

if __name__ == '__main__':
    app.run(debug=True, port=5000)