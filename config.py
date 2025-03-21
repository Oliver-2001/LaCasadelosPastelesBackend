from flask_sqlalchemy import SQLAlchemy
import urllib.parse

# Configuración de la conexión a SQL Server
server = "DESKTOP-GBK0OOI\\SQLEXPRESS"  
database = "CASADELOSPASTELES"
username = "AdminUser"  
password = "AdminUser"  

# Codificar las credenciales para la URL de conexión
params = urllib.parse.quote_plus(
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={server};"
    f"DATABASE={database};"
    f"UID={username};"
    f"PWD={password};"
    f"TrustServerCertificate=yes;"
)

# Crear la URI de conexión para SQLAlchemy
SQLALCHEMY_DATABASE_URI = f"mssql+pyodbc:///?odbc_connect={params}"

# Desactivar el seguimiento de modificaciones de SQLAlchemy para mejorar rendimiento
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Crear la instancia de SQLAlchemy
db = SQLAlchemy()

