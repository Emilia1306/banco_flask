import os

class Config:
    SECRET_KEY = "clave"  # Llave secreta para JWT
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost/banco'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
