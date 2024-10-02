import logging
from flask import Blueprint, request, redirect, url_for, render_template, flash, session
from werkzeug.security import check_password_hash
from models import Usuario
import jwt
import datetime

# Configuración del logging
logging.basicConfig(level=logging.DEBUG)  # Cambia a INFO o ERROR para menos detalle
logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form['correo']
        password = request.form['password']
        
        logger.debug(f'Intentando iniciar sesión con correo: {correo}')
        
        try:
            usuario = Usuario.query.filter_by(correo=correo).first()
            if usuario:
                logger.debug('Usuario encontrado en la base de datos.')
                
                if usuario.password == password: 
                    # Almacenar información del usuario en la sesión
                    session['usuario_id'] = usuario.id
                    session['rol'] = usuario.rol

                    # Generar un token JWT
                    token = jwt.encode({
                        'usuario_id': usuario.id,
                        'rol': usuario.rol,
                        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
                    }, 'clave', algorithm='HS256')

                    logger.debug(f'Token generado: {token}')

                    # Almacenar el token en las cookies
                    resp = redirect(url_for('main.dashboard'))
                    resp.set_cookie('token', token)

                    logger.info('Inicio de sesión exitoso, redirigiendo al dashboard.')
                    return resp
                else:
                    logger.warning('Contraseña incorrecta para el usuario: %s, contraseña ingresada: %s', correo, password)
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
    session.clear()
    logger.info('Usuario ha cerrado sesión.')
    return redirect(url_for('auth_bp.login'))