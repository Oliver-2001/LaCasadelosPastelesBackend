from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity
from config import SQLALCHEMY_DATABASE_URI  # Importa la URI de conexión
from models import db, Usuario  # Importa tu base de datos y modelo de usuario
from werkzeug.security import check_password_hash
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins="http://localhost:3000")

# Configuración de la base de datos
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "tu_clave_secreta"

# Inicialización de la base de datos y JWT
db.init_app(app)
jwt = JWTManager(app)

###################################################################################Rutas#############################################################

@app.route("/")
def home():
    return jsonify(message="Bienvenido a la API de la pastelería"), 200


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    usuario = data["usuario"]  # Cambiado de email a usuario
    password = data["password"]

    # Verificar si el usuario ya existe
    existing_user = Usuario.query.filter_by(usuario=usuario).first()  # Cambiado de email a usuario
    if existing_user:
        return jsonify(message="El usuario ya existe"), 400

    # Crear y guardar el nuevo usuario
    new_user = Usuario(usuario=usuario)  # Cambiado de email a usuario
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify(message="Usuario registrado exitosamente"), 201


# Ruta de inicio de sesión
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    usuario = data.get('usuario')
    contrasena = data.get('contrasena')

    # Buscar el usuario en la base de datos
    user = Usuario.query.filter_by(usuario=usuario).first()

    if user and check_password_hash(user.contrasena, contrasena):
        # Login exitoso
        return jsonify({"message": "Login exitoso"})
    else:
        # Usuario o contraseña incorrectos
        return jsonify({"message": "Usuario o contraseña incorrectos"}), 401

# Ruta protegida (requiere autenticación)
@app.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(message=f"Hola, {current_user}! Esta es una ruta protegida."), 200


if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Crear tablas si no existen
    app.run(debug=True)
