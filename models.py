from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Usuario(db.Model):
    __tablename__ = 'Usuarios'
    id_usuario = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    usuario = db.Column(db.String(50), unique=True, nullable=False)
    contrasena = db.Column(db.String(200), nullable=False)
    id_rol = db.Column(db.Integer, db.ForeignKey('Roles.id_rol'), nullable=False)
    rol = db.relationship('Rol', backref=db.backref('usuarios', lazy=True))

class Rol(db.Model):
    __tablename__ = 'Roles'
    id_rol = db.Column(db.Integer, primary_key=True)
    nombre_rol = db.Column(db.String(50), nullable=False)

class Modulo(db.Model):
    __tablename__ = 'Modulos'
    id_modulo = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(255))


class RolModulo(db.Model):
    __tablename__ = 'RolesModulos'
    id = db.Column(db.Integer, primary_key=True)
    id_rol = db.Column(db.Integer, db.ForeignKey('Roles.id_rol'), nullable=False)
    id_modulo = db.Column(db.Integer, db.ForeignKey('Modulos.id_modulo'), nullable=False)

    rol = db.relationship('Rol', backref=db.backref('modulos_asignados', lazy=True))
    modulo = db.relationship('Modulo', backref=db.backref('roles_asignados', lazy=True))