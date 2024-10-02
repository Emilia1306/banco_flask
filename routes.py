from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import Usuario, Cuenta, Movimiento
from database import db
import jwt
import logging

# Configuración del logging
logging.basicConfig(level=logging.DEBUG)  # Cambia a INFO o ERROR para menos detalle
logger = logging.getLogger(__name__)

main_bp = Blueprint('main', __name__)

@main_bp.route('/dashboard')
def dashboard():
    token = request.cookies.get('token')
    if not token:
        logger.warning('No se encontró el token, redirigiendo a login.')
        return redirect(url_for('auth_bp.login'))  # Redirigir al login si no hay token

    try:
        decoded = jwt.decode(token, 'clave', algorithms=['HS256'])
        usuario_id = decoded['usuario_id']
        rol = decoded['rol']

        logger.info(f'Usuario {usuario_id} con rol {rol} accediendo al dashboard.')

        if rol == 'admin':
            return render_template('dashboard_admin.html')
        else:
            cuenta = Cuenta.query.filter_by(usuario_id=usuario_id).first()
            saldo = cuenta.saldo if cuenta else 0.00
            return render_template('dashboard_usuario.html', saldo=saldo)

    except jwt.ExpiredSignatureError:
        logger.warning('Token ha expirado, redirigiendo a login.')
        return redirect(url_for('auth_bp.login'))
    
@main_bp.route('/editar_perfil', methods=['GET', 'POST'])
def editar_perfil():
    token = request.cookies.get('token')
    if not token:
        logger.warning('No se encontró el token, redirigiendo a login.')
        return redirect(url_for('auth_bp.login'))
    
    try:
        decoded = jwt.decode(token, 'clave', algorithms=['HS256'])
        usuario_id = decoded['usuario_id']
        usuario = Usuario.query.get(usuario_id)

        if request.method == 'POST':
            # Obtener los datos del formulario
            nombre = request.form['nombre']
            num_identificacion = request.form['num_identificacion']
            correo = request.form['correo']

            # Log de los datos recibidos
            logger.debug(f'Datos recibidos - Nombre: {nombre}, Num Identificación: {num_identificacion}, Correo: {correo}')

            # Actualizar los datos del usuario
            usuario.nombre = nombre
            usuario.num_identificacion = num_identificacion
            usuario.correo = correo
            
            # Guardar cambios en la base de datos
            db.session.commit()

            # Log de confirmación de actualización
            logger.info(f'Perfil del usuario ID {usuario_id} actualizado correctamente.')
            flash('Perfil actualizado correctamente.')
            return redirect(url_for('main.editar_perfil'))

        return render_template('editar_perfil.html', usuario=usuario)  # Asegúrate de tener esta plantilla

    except jwt.ExpiredSignatureError:
        flash('El token ha expirado, por favor inicie sesión nuevamente.')
        return redirect(url_for('auth_bp.login'))
    except jwt.InvalidTokenError:
        flash('Token inválido, por favor inicie sesión nuevamente.')
        return redirect(url_for('auth_bp.login'))
    except Exception as e:
        logger.error(f'Error al actualizar el perfil: {e}')
        flash('Ocurrió un error, por favor intenta nuevamente.')
        return redirect(url_for('main.dashboard'))

@main_bp.route('/ver_usuarios')
def ver_usuarios():
    token = request.cookies.get('token')
    if not token:
        return redirect(url_for('auth_bp.login'))  # Redirigir si no hay token
    usuarios = Usuario.query.all()
    return render_template('ver_usuarios.html', usuarios=usuarios)

@main_bp.route('/movimientos')
def movimientos():
    token = request.cookies.get('token')
    if not token:
        return redirect(url_for('auth_bp.login'))
    
    try:
        decoded = jwt.decode(token, 'clave', algorithms=['HS256'])
        usuario_id = decoded['usuario_id']
        movimientos = Movimiento.query.filter_by(usuario_id=usuario_id).all()
        return render_template('movimientos.html', movimientos=movimientos)
    except jwt.ExpiredSignatureError:
        flash('El token ha expirado, por favor inicie sesión nuevamente.')
        return redirect(url_for('auth_bp.login'))
    except jwt.InvalidTokenError:
        flash('Token inválido, por favor inicie sesión nuevamente.')
        return redirect(url_for('auth_bp.login'))

@main_bp.route('/transferir', methods=['GET', 'POST'])
def transferir():
    token = request.cookies.get('token')
    if not token:
        return redirect(url_for('auth_bp.login'))

    try:
        decoded = jwt.decode(token, 'clave', algorithms=['HS256'])
        usuario_id = decoded['usuario_id']
        cuenta_origen = Cuenta.query.filter_by(usuario_id=usuario_id).first()

        if request.method == 'POST':
            cuenta_origen_id = cuenta_origen.id  # Suponiendo que esta cuenta no es None
            cuenta_destino_id = request.form['cuenta_destino']
            monto = float(request.form['monto'])

            cuenta_destino = Cuenta.query.filter_by(id=cuenta_destino_id).first()

            if cuenta_origen.saldo >= monto:
                cuenta_origen.saldo -= monto
                cuenta_destino.saldo += monto

                movimiento = Movimiento(usuario_id=usuario_id, cuenta_origen=cuenta_origen_id, cuenta_destino=cuenta_destino.id, monto=monto, descripcion="Transferencia realizada")
                db.session.add(movimiento)

                try:
                    db.session.commit()
                    flash('Transferencia realizada correctamente.')
                    return redirect(url_for('main.dashboard'))
                except Exception as e:
                    logger.error(f'Error al guardar la transferencia: {e}')
                    flash('Ocurrió un error al procesar la transferencia. Intenta de nuevo.')

            else:
                flash('Fondos insuficientes.')

        return render_template('transferir.html', cuenta_origen=cuenta_origen)

    except jwt.ExpiredSignatureError:
        flash('El token ha expirado, por favor inicie sesión nuevamente.')
        return redirect(url_for('auth_bp.login'))
    except jwt.InvalidTokenError:
        flash('Token inválido, por favor inicie sesión nuevamente.')
        return redirect(url_for('auth_bp.login'))
    except Exception as e:
        logger.error(f'Error inesperado: {e}')
        flash('Ocurrió un error inesperado. Por favor intenta nuevamente.')
