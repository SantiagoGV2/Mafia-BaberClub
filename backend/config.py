import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Config:
    # Configuración de la base de datos
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '12345')
    MYSQL_DB = os.getenv('MYSQL_DB', 'barberia_db')
    
    # Configuración de JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', '1011084605')
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hora
    
    # Configuración de la aplicación
    SECRET_KEY = os.getenv('SECRET_KEY', '001205')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true' 