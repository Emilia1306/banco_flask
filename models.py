from database import get_db_connection

class Usuario:
    @staticmethod
    def get_usuario_by_id(usuario_id):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM usuarios WHERE id = %s', (usuario_id,))
        usuario = cursor.fetchone()
        cursor.close()
        conn.close()
        return usuario

    @staticmethod
    def update_usuario(usuario_id, nombre, num_identificacion, correo):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE usuarios SET nombre = %s, num_identificacion = %s, correo = %s WHERE id = %s',
                       (nombre, num_identificacion, correo, usuario_id))
        conn.commit()
        cursor.close()
        conn.close()

class Cuenta:
    @staticmethod
    def get_cuenta_by_usuario_id(usuario_id):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM cuentas WHERE usuario_id = %s', (usuario_id,))
        cuenta = cursor.fetchone()
        cursor.close()
        conn.close()
        return cuenta

    @staticmethod
    def get_cuenta_by_id(cuenta_id):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM cuentas WHERE id = %s', (cuenta_id,))
        cuenta = cursor.fetchone()
        cursor.close()
        conn.close()
        return cuenta
    
    @staticmethod
    def update_saldo(cuenta_id, nuevo_saldo):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE cuentas SET saldo = %s WHERE id = %s', (nuevo_saldo, cuenta_id))
        conn.commit()
        cursor.close()
        conn.close()

class Movimiento:
    @staticmethod
    def add_movimiento(usuario_id, cuenta_origen, cuenta_destino, monto, descripcion):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO movimientos (usuario_id, cuenta_origen, cuenta_destino, monto, descripcion) VALUES (%s, %s, %s, %s, %s)',
                       (usuario_id, cuenta_origen, cuenta_destino, monto, descripcion))
        conn.commit()
        cursor.close()
        conn.close()
