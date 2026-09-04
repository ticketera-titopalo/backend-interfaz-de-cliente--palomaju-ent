import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv
from sqlalchemy import text

# 1. Cargar variables de entorno
load_dotenv(dotenv_path="../.env")

print("--- INICIANDO CONFIGURACIÓN DEL SERVIDOR ---")

app = Flask(__name__)

# Configuración de CORS
CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}})

# Configuración de la Base de Datos
user = os.getenv('MYSQL_USER')
password = os.getenv('MYSQL_PASSWORD')
db_name = os.getenv('MYSQL_DATABASE')
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{user}:{password}@localhost:3306/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo de Datos
class Concert(db.Model):
    __tablename__ = 'concerts'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    date = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.String(255), nullable=True)

# Crear tablas y datos de prueba
with app.app_context():
    print("Verificando base de datos...")
    db.create_all()
    if Concert.query.count() == 0:
        print("Insertando datos de prueba...")
        c1 = Concert(name="Duki", date="2024-12-10", price=45000, stock=100)
        c2 = Concert(name="Wos", date="2024-11-15", price=35000, stock=50)
        db.session.add_all([c1, c2])
        db.session.commit()
    print("Base de datos lista.")

# Endpoints
@app.route('/api/status', methods=['GET'])
def get_status():
    db.session.execute(text('SELECT 1'))
    return jsonify({"status": "online", "database": "connected"}), 200

@app.route('/api/concerts', methods=['GET'])
def get_concerts():
    concerts = Concert.query.all()
    return jsonify([{"id": c.id, "name": c.name, "stock": c.stock} for c in concerts]), 200

@app.route('/api/purchase', methods=['POST'])
def purchase_ticket():
    try:
        data = request.get_json()
        concert_id = data.get('concert_id')
        quantity = data.get('quantity', 1)

        # 1. Buscar el concierto
        concert = Concert.query.get(concert_id)

        if not concert:
            return jsonify({"message": "Concierto no encontrado"}), 404

        # 2. VALIDACIÓN CRUCIAL: ¿Hay suficiente para lo que pide el cliente?
        if concert.stock < quantity:
            return jsonify({
                "message": "Stock insuficiente", 
                "stock_disponible": concert.stock,
                "solicitado": quantity
            }), 400  # <--- Ahora sí devuelve 400 si no alcanza

        # 3. Solo si pasa la validación, restamos
        concert.stock -= quantity
        db.session.commit()

        return jsonify({
            "message": "Compra realizada con éxito",
            "concierto": concert.name,
            "nuevo_stock": concert.stock
        }), 200

    except Exception as e:
        db.session.rollback() # Si algo falla en la base de datos, cancela la operación
        return jsonify({"error": str(e)}), 500

# ESTA PARTE ES LA MÁS IMPORTANTE: debe estar al ras de la izquierda
if __name__ == '__main__':
    print("--- SERVIDOR CORRIENDO EN PORT 5000 ---")
    app.run(debug=True, port=5000)