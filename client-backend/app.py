import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv
from sqlalchemy import text 

# Cargar variables desde el archivo .env ubicado en la raíz (un nivel arriba)
load_dotenv(dotenv_path="../.env")

app = Flask(__name__)

# Configuración de CORS: Permite que el futuro React (puerto 5173) haga peticiones
CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}})

# Configuración de la Base de Datos
user = os.getenv('MYSQL_USER')
password = os.getenv('MYSQL_PASSWORD')
host = 'localhost' # Desde tu PC hacia el contenedor de Docker
port = '3306'
db_name = os.getenv('MYSQL_DATABASE')

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar SQLAlchemy
db = SQLAlchemy(app)

# --- Endpoint de Prueba (Issue #02 Tarea 4) ---
@app.route('/api/status', methods=['GET'])
def get_status():
    try:
        # Intenta una consulta simple a la DB para verificar conexión
        db.session.execute(text('SELECT 1'))
        return jsonify({
            "status": "online",
            "database": "connected",
            "message": "Backend de la Ticketera funcionando correctamente"
        }), 200
    except Exception as e:
        return jsonify({
            "status": "online",
            "database": "disconnected",
            "error": str(e)
        }), 500

if __name__ == '__main__':
    # El puerto 5000 es el estándar de Flask
    app.run(debug=True, port=5000)