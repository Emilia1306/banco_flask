from flask import Flask
from models import db
from config import Config
from auth import auth_bp
from routes import main_bp
import logging

# Configuración del logging
logging.basicConfig(level=logging.DEBUG)  # Cambia a INFO o ERROR para menos detalle
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)

# Inicializar la base de datos
db.init_app(app)

# Crear las tablas si no existen
with app.app_context():
    db.create_all()
    logger.info('Tablas creadas o ya existen en la base de datos.')

# Registrar Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)

if __name__ == '__main__':
    app.run(debug=True)
