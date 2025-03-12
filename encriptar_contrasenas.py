from werkzeug.security import generate_password_hash
from app import app, db  # Importa la app y db
from models import Usuario  # Asegúrate de importar el modelo de Usuario

# Iniciar el contexto de la aplicación Flask
with app.app_context():
    # Obtener todos los usuarios
    usuarios = Usuario.query.all()

    # Iterar sobre los usuarios y encriptar sus contraseñas
    for usuario in usuarios:
        # Encriptar la contraseña
        usuario.contrasena = generate_password_hash(usuario.contrasena)
        db.session.commit()  # Guardar los cambios en la base de datos

    print("Contraseñas encriptadas y actualizadas.")
