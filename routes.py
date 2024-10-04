from flask import Blueprint, render_template, request, redirect, url_for, flash
import jwt
import logging
from models import Usuario, Cuenta, Movimiento
from database import get_db_connection
from decimal import Decimal

# Configuración del logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

main_bp = Blueprint('main', __name__)

@main_bp.route('/dashboard')
def dashboard():
    token = request.cookies.get('token')
    if not token:
        logger.warning('No se encontró el token, redirigiendo a login.')
        return redirect(url_for('auth_bp.login'))

    try:
        decoded = jwt.decode(token, 'clave', algorithms=['HS256'])
        usuario_id = decoded['usuario_id']
        rol = decoded['rol']

        logger.info(f'Usuario {usuario_id} con rol {rol} accediendo al dashboard.')

        connection = get_db_connection()

        if rol == 'admin':
            # Obtener la lista de usuarios para el administrador
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM usuarios")
                usuarios = cursor.fetchall()  # Obtener todos los usuarios

            return render_template('dashboard_admin.html', usuarios=usuarios)

        else:
            # Para usuarios normales, obtener su saldo
            with connection.cursor(dictionary=True) as cursor:
                sql = "SELECT * FROM cuentas WHERE usuario_id = %s"
                cursor.execute(sql, (usuario_id,))
                cuenta = cursor.fetchone()

            if cuenta is None:
                logger.error(f'No se encontró la cuenta para el usuario ID {usuario_id}.')
                saldo = 0.00
            else:
                saldo = cuenta['saldo']

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
        logger.debug(f'Usuario ID: {usuario_id}')

        usuario = Usuario.get_usuario_by_id(usuario_id)
        logger.debug(f'Usuario recuperado: {usuario}')

        if not usuario:
            logger.error(f'No se encontró el usuario con ID: {usuario_id}')
            flash('No se encontró el usuario. Por favor intenta nuevamente.')
            return redirect(url_for('main.dashboard'))

        if request.method == 'POST':
            nombre = request.form['nombre']
            # Verificar si el nombre parece ser una expresión
            if nombre.startswith("{{") and nombre.endswith("}}"):
                try:
                    # Evaluar la expresión, eliminando las llaves
                    nombre = eval(nombre[2:-2].strip())
                except Exception as e:
                    logger.error(f'Error al evaluar la expresión: {e}')
                    # Manejar el error, quizás asignando un valor por defecto
                    nombre = "Error en la expresión"

            num_identificacion = request.form['num_identificacion']
            correo = request.form['correo']

            # Agrega el logger aquí para depurar el nombre
            logger.debug(f'Nombre a guardar: {nombre}')  # <--- Aquí

            logger.debug(f'Datos recibidos - Nombre: {nombre}, Num Identificación: {num_identificacion}, Correo: {correo}')

            Usuario.update_usuario(usuario_id, nombre, num_identificacion, correo)

            logger.info(f'Perfil del usuario ID {usuario_id} actualizado correctamente.')
            flash('Perfil actualizado correctamente.')
            return redirect(url_for('main.editar_perfil'))

        logger.debug(f'Preparando la vista de edición para el usuario: {usuario}')
        return render_template('editar_perfil.html', usuario=usuario)

    except jwt.ExpiredSignatureError:
        flash('El token ha expirado, por favor inicie sesión nuevamente.')
        return redirect(url_for('auth_bp.login'))
    except jwt.InvalidTokenError:
        flash('Token inválido, por favor inicie sesión nuevamente.')
        return redirect(url_for('auth_bp.login'))


    except jwt.ExpiredSignatureError:
        flash('El token ha expirado, por favor inicie sesión nuevamente.')
        return redirect(url_for('auth_bp.login'))
    except jwt.InvalidTokenError:
        flash('Token inválido, por favor inicie sesión nuevamente.')
        return redirect(url_for('auth_bp.login'))


@main_bp.route('/ver_usuarios')
def ver_usuarios():
    token = request.cookies.get('token')
    if not token:
        return redirect(url_for('auth_bp.login'))  # Redirigir si no hay token

    connection = get_db_connection()
    with connection.cursor() as cursor:
        sql = "SELECT * FROM usuarios"
        cursor.execute(sql)
        usuarios = cursor.fetchall()

    return render_template('ver_usuarios.html', usuarios=usuarios)

@main_bp.route('/movimientos')
def movimientos():
    token = request.cookies.get('token')
    if not token:
        return redirect(url_for('auth_bp.login'))

    try:
        decoded = jwt.decode(token, 'clave', algorithms=['HS256'])
        usuario_id = decoded['usuario_id']

        connection = get_db_connection()
        with connection.cursor(dictionary=True) as cursor:
            sql = "SELECT * FROM movimientos WHERE usuario_id = %s"
            cursor.execute(sql, (usuario_id,))
            movimientos = cursor.fetchall()
            logger.debug(f'Movimientos obtenidos: {movimientos}')  # Log para verificar datos

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
        logger.warning('No se encontró el token, redirigiendo a login.')
        return redirect(url_for('auth_bp.login'))

    try:
        decoded = jwt.decode(token, 'clave', algorithms=['HS256'])
        usuario_id = decoded['usuario_id']
        logger.info(f'Usuario ID {usuario_id} ha sido autenticado.')

        cuenta_origen = Cuenta.get_cuenta_by_usuario_id(usuario_id)
        if not cuenta_origen:
            logger.error(f'No se encontró la cuenta de origen para el usuario ID {usuario_id}.')
            flash('No se encontró la cuenta de origen.')
            return redirect(url_for('main.dashboard'))

        if request.method == 'POST':
            cuenta_origen_id = cuenta_origen['id']
            cuenta_destino_id = request.form['cuenta_destino']
            monto = Decimal(request.form['monto'])  # Asegúrate de que esto sea Decimal

            logger.debug(f'Transferir de cuenta {cuenta_origen_id} a cuenta {cuenta_destino_id} un monto de {monto}.')

            cuenta_destino = Cuenta.get_cuenta_by_id(cuenta_destino_id)
            if not cuenta_destino:
                logger.error(f'No se encontró la cuenta de destino ID {cuenta_destino_id}.')
                flash('No se encontró la cuenta de destino.')
                return redirect(url_for('main.dashboard'))

            saldo_origen = Decimal(cuenta_origen['saldo'])

            if saldo_origen >= monto:
                logger.info(f'Fondos suficientes para realizar la transferencia. Saldo origen: {saldo_origen}, Monto: {monto}.')
                
                # Actualizar saldos en la base de datos
                # Resta el monto de la cuenta de origen
                Cuenta.update_saldo(cuenta_origen_id, saldo_origen - monto)
                # Suma el monto a la cuenta de destino
                Cuenta.update_saldo(cuenta_destino_id, Decimal(cuenta_destino['saldo']) + monto)

                # Guardar movimiento
                Movimiento.add_movimiento(usuario_id, cuenta_origen_id, cuenta_destino['id'], monto, "Transferencia realizada")

                logger.info('Transferencia realizada correctamente.')
                flash('Transferencia realizada correctamente.')
                return redirect(url_for('main.dashboard'))
            else:
                logger.warning('Fondos insuficientes para realizar la transferencia.')
                flash('Fondos insuficientes.')

        return render_template('transferir.html', cuenta_origen=cuenta_origen)

    except jwt.ExpiredSignatureError:
        logger.warning('El token ha expirado, redirigiendo a login.')
        flash('El token ha expirado, por favor inicie sesión nuevamente.')
        return redirect(url_for('auth_bp.login'))
    except jwt.InvalidTokenError:
        logger.warning('Token inválido, redirigiendo a login.')
        flash('Token inválido, por favor inicie sesión nuevamente.')
        return redirect(url_for('auth_bp.login'))
    except Exception as e:
        logger.error(f'Error inesperado: {e}')
        flash('Ocurrió un error inesperado. Por favor intenta nuevamente.')
        return redirect(url_for('main.dashboard'))

