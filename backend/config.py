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

    #Configuracion Correos
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', 'false').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_USERNAME') # El remitente será tu mismo correo