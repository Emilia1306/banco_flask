import mysql.connector
from mysql.connector import Error

def get_db_connection():
    connection = None
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',  # Cambia esto si tienes una contraseña
            database='banco'
        )
        if connection.is_connected():
            print("Conexión exitosa a la base de datos")
    except Error as e:
        print(f"Error: '{e}'")

    return connection
