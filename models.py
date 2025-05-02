from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

ROLES = {
    1: "superadmin",
    2: "admin",
    3: "cajero",
    4: "panadero"
}

class Usuario(db.Model):
    __tablename__ = 'Usuarios'
    id_usuario = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    usuario = db.Column(db.String(50), unique=True, nullable=False)
    contrasena = db.Column(db.String(200), nullable=False)
    id_rol = db.Column(db.Integer, db.ForeignKey('Roles.id_rol'), nullable=False)
    
    # Relación con el rol
    rol = db.relationship('Rol', backref=db.backref('usuarios', lazy=True))

    # Método para hashear la contraseña
    def set_password(self, password):
        self.contrasena = generate_password_hash(password)

    # Método para verificar la contraseña
    def check_password(self, password):
        return check_password_hash(self.contrasena, password)


class Rol(db.Model):
    __tablename__ = 'Roles'
    id_rol = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)

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


class Producto(db.Model):
    __tablename__ = 'Productos'  # Nombre de la tabla en la base de datos

    id_producto = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    categoria = db.Column(db.String(50), nullable=False)

    def __init__(self, nombre, precio, stock, categoria):
        self.nombre = nombre
        self.precio = precio
        self.stock = stock
        self.categoria = categoria

class Inventario(db.Model):
    __tablename__ = 'Inventario'

    id_insumo = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    unidad = db.Column(db.String(50), nullable=False)
    fecha_actualizacion = db.Column(db.DateTime, nullable=False)
    id_sucursal = db.Column(db.Integer, nullable=False)

    def __init__(self, nombre, cantidad, unidad, fecha_actualizacion, id_sucursal):
        self.nombre = nombre
        self.cantidad = cantidad
        self.unidad = unidad
        self.fecha_actualizacion = fecha_actualizacion
        self.id_sucursal = id_sucursal