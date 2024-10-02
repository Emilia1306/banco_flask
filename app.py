from flask import Flask
from config import Config
from auth import auth_bp
from routes import main_bp
import logging

# Configuración del logging
logging.basicConfig(level=logging.DEBUG)  # Cambia a INFO o ERROR para menos detalle
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)

# Aquí no necesitas inicializar la base de datos ni crear tablas,
# ya que estás usando conexión directa a través de mysql.connector.

# Registrar Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)

if __name__ == '__main__':
    app.run(debug=True)
