from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config

# Crear la aplicación Flask
app = Flask(__name__)
app.config.from_object(Config)

# Configurar CORS
CORS(app)

# Configurar JWT
jwt = JWTManager(app)

# Importar rutas
from routes.auth import auth_bp
from routes.barberos import barberos_bp
from routes.clientes import clientes_bp
from routes.servicios import servicios_bp
from routes.reservas import reservas_bp

# Registrar blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(barberos_bp, url_prefix='/api/barberos')
app.register_blueprint(clientes_bp, url_prefix='/api/clientes')
app.register_blueprint(servicios_bp, url_prefix='/api/servicios')
app.register_blueprint(reservas_bp, url_prefix='/api/reservas')

if __name__ == '__main__':
    app.run(debug=Config.DEBUG) 