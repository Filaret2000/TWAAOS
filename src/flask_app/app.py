import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_swagger_ui import get_swaggerui_blueprint
import json

# Inițializare aplicație Flask
app = Flask(__name__)

# Configurare aplicație
app.config.from_object('src.flask_app.config.Config')

# Inițializare extensii
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
jwt = JWTManager(app)
CORS(app)

# Configurare Swagger UI
SWAGGER_URL = '/api/docs/flask'
API_URL = '/api/swagger.json'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Sistem Planificare Examene FIESC - Flask API"
    }
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Încărcare swagger.json
@app.route('/api/swagger.json')
def swagger_spec():
    with open(os.path.join(os.path.dirname(__file__), 'swagger.json'), 'r') as f:
        return jsonify(json.load(f))

# Inițializare bază de date
from src.flask_app.utils.db import init_db
init_db(app)

# Înregistrare rute
from src.flask_app.routes import register_routes
register_routes(app)

# Endpoint pentru verificarea sănătății
@app.route('/api/health')
def health_check():
    return jsonify({"status": "ok"})

# Pagină de eroare 404
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404

# Pagină de eroare 500
@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Server error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
