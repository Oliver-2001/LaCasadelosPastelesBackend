from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity
from config import SQLALCHEMY_DATABASE_URI  # Importa la URI de conexión
from models import db, Usuario, Rol, Modulo, RolModulo, Producto, Inventario  # Importa tu base de datos y modelo de usuario
from werkzeug.security import check_password_hash, generate_password_hash
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins="http://localhost:3000")

# Configuración de la base de datos
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "Or005836434*"
app.config["JWT_SECRET_KEY"] = "OR005836434*"

# Inicialización de la base de datos y JWT
db.init_app(app)
jwt = JWTManager(app)

###################################################################################Rutas#############################################################

@app.route("/")
def home():
    return jsonify(message="Bienvenido a la API de la pastelería"), 200

# ############################################# Ruta de inicio de sesión #############################################
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    usuario = data.get('usuario')
    contrasena = data.get('contrasena')

    user = Usuario.query.filter_by(usuario=usuario).first()

    if user and check_password_hash(user.contrasena, contrasena):
        # ✅ Genera el token JWT
        token = create_access_token(identity=str(user.id_usuario))  # Guarda el ID del usuario en el token
        return jsonify({
            "message": "Login exitoso",
            "token": token
        }), 200
    else:
        return jsonify({"message": "Usuario o contraseña incorrectos"}), 401
    

############################################## Ruta protegida (requiere autenticación)#############################################
@app.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(message=f"Hola, {current_user}! Esta es una ruta protegida."), 200

# Ruta para obtener los modulos del usuario autenticado
@app.route('/modulos', methods=['GET'])
@jwt_required()
def obtener_modulos():
    current_user_id = get_jwt_identity() 
    usuario = Usuario.query.filter_by(id_usuario=current_user_id).first()  

    if not usuario:
        return jsonify({"message": "Usuario no encontrado"}), 404

    # Obtener los módulos a los que el usuario tiene acceso
    modulos = Modulo.query.join(RolModulo).filter(RolModulo.id_rol == usuario.id_rol).all()

    modulos_list = [{"id_modulo": modulo.id_modulo, "nombre": modulo.nombre, "descripcion": modulo.descripcion} for modulo in modulos]

    return jsonify(modulos_list), 200


############################################## Ruta para obtener todos los usuarios (solo accesible por admins) (Modulo Admin de Usuarios) #############################################
@app.route('/usuarios', methods=['GET'])
@jwt_required()
def obtener_usuarios():
    current_user_id = get_jwt_identity()
    usuario = Usuario.query.filter_by(id_usuario=current_user_id).first()

    if not usuario:
        return jsonify({"message": "Usuario no encontrado"}), 404

    if usuario.id_rol != 1:  
        return jsonify({"message": "No tienes permisos para acceder a esta información"}), 403

    # Obtener todos los usuarios 
    usuarios = Usuario.query.all()
    usuarios_list = [{"id_usuario": u.id_usuario, "nombre": u.nombre, "usuario": u.usuario, "rol": u.id_rol} for u in usuarios]

    return jsonify(usuarios_list), 200

################################################## Ruta para eliminar usuarios (Modulo Admin de Usuarios) #############################################
@app.route('/usuarios/<int:id_usuario>', methods=['DELETE'])
@jwt_required()
def eliminar_usuario(id_usuario):
    current_user_id = get_jwt_identity()
    usuario_actual = Usuario.query.filter_by(id_usuario=current_user_id).first()

    if not usuario_actual:
        return jsonify({"message": "Usuario no encontrado"}), 404

    if usuario_actual.id_rol != 1:  
        return jsonify({"message": "No tienes permisos para eliminar usuarios"}), 403

    usuario = Usuario.query.filter_by(id_usuario=id_usuario).first()

    if not usuario:
        return jsonify({"message": "El usuario no existe"}), 404

    if usuario.id_rol == 1:
        return jsonify({"message": "No se puede eliminar al Superadmin"}), 403

    db.session.delete(usuario)
    db.session.commit()

    return jsonify({"message": "Usuario eliminado correctamente"}), 200


################################# Ruta para editar usuarios (Modulo Admin de Usuarios) #############################################
@app.route('/usuarios/<int:id_usuario>', methods=['PUT'])
@jwt_required()
def editar_usuario(id_usuario):
    current_user_id = get_jwt_identity()
    usuario_actual = Usuario.query.filter_by(id_usuario=current_user_id).first()

    if not usuario_actual:
        return jsonify({"message": "Usuario no encontrado"}), 404

    if usuario_actual.id_rol != 1:
        return jsonify({"message": "No tienes permisos para modificar usuarios"}), 403

    usuario = Usuario.query.filter_by(id_usuario=id_usuario).first()
    if not usuario:
        return jsonify({"message": "Usuario no encontrado"}), 404

    data = request.get_json()
    nombre = data.get("nombre")
    usuario_nombre = data.get("usuario")
    id_rol = data.get("id_rol")

    if not nombre or not usuario_nombre or not id_rol:
        return jsonify({"message": "Todos los campos son obligatorios"}), 400

    if id_rol not in [1, 2, 3, 4]:
        return jsonify({"message": "Rol no válido"}), 400

    usuario_existente = Usuario.query.filter_by(usuario=usuario_nombre).first()
    if usuario_existente and usuario_existente.id_usuario != id_usuario:
        return jsonify({"message": "El nombre de usuario ya está en uso"}), 400

    usuario.nombre = nombre
    usuario.usuario = usuario_nombre
    usuario.id_rol = id_rol

    db.session.commit()

    return jsonify({"message": "Usuario actualizado correctamente"}), 200

######################################### Ruta para crear usuarios nuevos (Modulo Admin de Usuarios) #############################################
@app.route('/api/usuarios', methods=['POST'])
def crear_usuario():
    data = request.get_json()

    # Validar que se envíen todos los campos
    if not data.get('nombre') or not data.get('usuario') or not data.get('contrasena') or not data.get('id_rol'):
        return jsonify({'error': 'Faltan datos obligatorios'}), 400

    # Verificar que el id_rol sea válido
    rol = Rol.query.get(data['id_rol'])
    if not rol:
        return jsonify({'error': 'Rol no válido'}), 400

    # Crear el nuevo usuario
    nuevo_usuario = Usuario(
        nombre=data['nombre'],
        usuario=data['usuario'],
        contrasena=generate_password_hash(data['contrasena']),
        id_rol=data['id_rol']
    )

    try:
        db.session.add(nuevo_usuario)
        db.session.commit()
        return jsonify({
            'mensaje': 'Usuario creado con éxito',
            'usuario': {
                'id_usuario': nuevo_usuario.id_usuario,
                'nombre': nuevo_usuario.nombre,
                'usuario': nuevo_usuario.usuario,
                'rol': rol.nombre_rol
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    


################################################################## Modulo Productos ##############################################################
@app.route('/productos', methods=['GET'])
@jwt_required()
def obtener_productos():
    current_user_id = get_jwt_identity()

    usuario = Usuario.query.filter_by(id_usuario=current_user_id).first()

    if not usuario:
        return jsonify({"message": "Usuario no encontrado"}), 404

    # Obtener todos los productos
    productos = Producto.query.all() 

    productos_list = [
        {
            "id_producto": p.id_producto,
            "nombre": p.nombre,
            "precio": p.precio,
            "stock": p.stock,
            "categoria": p.categoria
        } for p in productos
    ]

    return jsonify(productos_list), 200



##############(EDITAR) Modulo Productos #############################


@app.route('/productos/<int:id_producto>', methods=['PUT'])
@jwt_required()
def editar_producto(id_producto):
    current_user_id = get_jwt_identity()
    usuario = Usuario.query.filter_by(id_usuario=current_user_id).first()

    if not usuario:
        return jsonify({"message": "Usuario no encontrado"}), 404

    if usuario.rol.nombre not in ['superadmin', 'admin']:  
        return jsonify({"message": "No tiene permisos para editar productos"}), 403

    producto = Producto.query.get(id_producto)
    if not producto:
        return jsonify({"message": "Producto no encontrado"}), 404

    # Obtener los datos enviados en el cuerpo de la solicitud
    data = request.get_json()

    # Actualizar los campos del producto
    producto.nombre = data.get('nombre', producto.nombre)
    producto.precio = data.get('precio', producto.precio)
    producto.stock = data.get('stock', producto.stock)
    producto.categoria = data.get('categoria', producto.categoria)

    db.session.commit()

    return jsonify({"message": "Producto actualizado correctamente"}), 200


##############(Eliminar) Modulo Productos ########################################

@app.route('/productos/<int:id_producto>', methods=['DELETE'])
@jwt_required()
def eliminar_producto(id_producto):
    current_user_id = get_jwt_identity()
    usuario = Usuario.query.filter_by(id_usuario=current_user_id).first()

    if not usuario:
        return jsonify({"message": "Usuario no encontrado"}), 404

    # Accede a 'nombre_rol' ya que tu clase Rol tiene esa columna
    if usuario.rol.nombre not in ['superadmin', 'admin']:  
        return jsonify({"message": "No tiene permisos para eliminar productos"}), 403

    producto = Producto.query.get(id_producto)
    if not producto:
        return jsonify({"message": "Producto no encontrado"}), 404

    db.session.delete(producto)
    db.session.commit()

    return jsonify({"message": "Producto eliminado correctamente"}), 200


################################################################## Modulo Inventario ##############################################################
@app.route('/inventario', methods=['GET'])
@jwt_required()
def obtener_inventario():
    # Obtén el ID del usuario autenticado
    current_user_id = get_jwt_identity()
    usuario = Usuario.query.filter_by(id_usuario=current_user_id).first()

    if not usuario:
        return jsonify({"message": "Usuario no encontrado"}), 404

    # Obtener todos los registros de inventario sin el ID de insumo
    inventarios = Inventario.query.all()
    inventarios_list = [
        {
            "nombre": inventario.nombre,
            "cantidad": inventario.cantidad,
            "unidad": inventario.unidad,
            "fecha_actualizacion": inventario.fecha_actualizacion,
            "id_sucursal": inventario.id_sucursal
        } for inventario in inventarios
    ]

    return jsonify(inventarios_list), 200

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  
    app.run(debug=True)