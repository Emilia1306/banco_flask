from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    num_identificacion = db.Column(db.String(20), nullable=False)
    correo = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), nullable=False)

    cuentas = db.relationship('Cuenta', backref='usuario', lazy=True)

class Cuenta(db.Model):
    __tablename__ = 'cuentas'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    saldo = db.Column(db.Float, nullable=False)
    pin = db.Column(db.String(4), nullable=False)

    movimientos_origen = db.relationship('Movimiento', foreign_keys='Movimiento.cuenta_origen', backref='cuenta_origen_rel', lazy=True)
    movimientos_destino = db.relationship('Movimiento', foreign_keys='Movimiento.cuenta_destino', backref='cuenta_destino_rel', lazy=True)

class Movimiento(db.Model):
    __tablename__ = 'movimientos'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    cuenta_origen = db.Column(db.Integer, db.ForeignKey('cuentas.id'), nullable=False)
    cuenta_destino = db.Column(db.Integer, db.ForeignKey('cuentas.id'), nullable=False)
    monto = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    descripcion = db.Column(db.String(255), nullable=False)
