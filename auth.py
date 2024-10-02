import logging
from flask import Blueprint, request, redirect, url_for, render_template, flash, session
import jwt
import datetime
from database import get_db_connection

# Configuración del logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form['correo']
        password = request.form['password']
        
        logger.debug(f'Intentando iniciar sesión con correo: {correo}')
        
        try:
            connection = get_db_connection()
            with connection.cursor() as cursor:
                sql = "SELECT * FROM usuarios WHERE correo = %s"
                cursor.execute(sql, (correo,))
                usuario = cursor.fetchone()
                
            if usuario:
                logger.debug('Usuario encontrado en la base de datos.')
                
                if usuario[4] == password:  # Asegúrate de que este índice corresponde a la columna de password
                    session['usuario_id'] = usuario[0]  # ID
                    session['rol'] = usuario[5]  # Rol

                    token = jwt.encode({
                        'usuario_id': usuario[0],
                        'rol': usuario[5],
                        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
                    }, 'clave', algorithm='HS256')

                    logger.debug(f'Token generado: {token}')

                    resp = redirect(url_for('main.dashboard'))
                    resp.set_cookie('token', token)

                    logger.info('Inicio de sesión exitoso, redirigiendo al dashboard.')
                    return resp
                else:
                    logger.warning('Contraseña incorrecta para el usuario: %s', correo)
                    flash('Usuario o contraseña incorrectos. Por favor, intenta de nuevo.')
            else:
                logger.warning('No se encontró el usuario con correo: %s', correo)
                flash('Usuario o contraseña incorrectos. Por favor, intenta de nuevo.')

        except Exception as e:
            logger.error(f'Error al consultar la base de datos: {e}')
            flash('Ocurrió un error, por favor intenta más tarde.')

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()  # Limpiar la sesión
    logger.info('Usuario ha cerrado sesión.')
    return redirect(url_for('auth_bp.login'))
