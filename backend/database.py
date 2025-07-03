# En backend/database.py

import mysql.connector
from mysql.connector import pooling, Error
from config import Config

class Database:
    _instance = None
    _pool = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            try:
                # En lugar de una sola conexión, creamos un pool de conexiones
                cls._pool = pooling.MySQLConnectionPool(
                    pool_name="barberia_pool",
                    pool_size=5,  # Número de conexiones que pueden estar abiertas
                    host=Config.MYSQL_HOST,
                    user=Config.MYSQL_USER,
                    password=Config.MYSQL_PASSWORD,
                    database=Config.MYSQL_DB
                )
                print("Pool de conexiones a la base de datos creado exitosamente.")
            except Error as e:
                print(f"Error al crear el pool de conexiones: {e}")
                raise
        return cls._instance

    def execute_query(self, query, params=None):
        cnx = None  # Inicializamos la conexión en None
        cursor = None # Inicializamos el cursor en None
        try:
            # Pedimos una conexión del pool
            cnx = self._pool.get_connection()
            
            # Usamos esa conexión específica para esta consulta
            cursor = cnx.cursor(dictionary=True)
            cursor.execute(query, params or ())
            
            if query.strip().upper().startswith('SELECT'):
                result = cursor.fetchall()
            else:
                cnx.commit()
                result = cursor.lastrowid
            
            return result

        except Error as e:
            print(f"Error al ejecutar la consulta: {e}")
            raise

        finally:
            # MUY IMPORTANTE: Devolvemos la conexión al pool cuando terminamos
            if cursor:
                cursor.close()
            if cnx and cnx.is_connected():
                cnx.close() # En un pool, .close() no la cierra, la devuelve al pool.
                # print("Conexión devuelta al pool.") # Puedes descomentar esto para depurar

# Crear una instancia global de la base de datos
db = Database()