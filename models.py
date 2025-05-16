from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime   
from sqlalchemy.orm import relationship

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
    __tablename__ = 'Productos'

    id_producto = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    categoria = db.Column(db.String(50), nullable=False)

    predicciones = db.relationship("PrediccionesIA", cascade="all, delete-orphan", back_populates="producto")

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

class Venta(db.Model):
    __tablename__ = 'Ventas'
    id_venta = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, default=datetime.now)
    total = db.Column(db.Float)
    id_usuario = db.Column(db.Integer, nullable=False)

class DetalleVenta(db.Model):
    __tablename__ = 'DetallesVenta'
    id_detalle = db.Column(db.Integer, primary_key=True)
    id_venta = db.Column(db.Integer, db.ForeignKey('Ventas.id_venta'), nullable=False)
    id_producto = db.Column(db.Integer, db.ForeignKey('Productos.id_producto'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    subtotal = db.Column(db.Float)

class Sucursal(db.Model):
    __tablename__ = 'Sucursales'

    id_sucursal = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(200), nullable=False)
    latitud = db.Column(db.Float, nullable=True)   # puede venir en blanco
    longitud = db.Column(db.Float, nullable=True)

    # Relación con predicciones
    predicciones = db.relationship('PrediccionesIA', back_populates='sucursal')

    def __repr__(self):
        return f"<Sucursal {self.nombre}>"
    

class PrediccionesIA(db.Model):
    __tablename__ = 'PrediccionesIA'

    id_prediccion = db.Column(db.Integer, primary_key=True)
    id_producto = db.Column(db.Integer, db.ForeignKey('Productos.id_producto'), nullable=False)
    fecha_prediccion = db.Column(db.Date, nullable=False)
    cantidad_prediccion = db.Column(db.Float, nullable=False)
    id_sucursal = db.Column(db.Integer, db.ForeignKey('Sucursales.id_sucursal'), nullable=False)

    # Relaciones
    producto = db.relationship('Producto', back_populates='predicciones')
    sucursal = db.relationship('Sucursal', back_populates='predicciones')