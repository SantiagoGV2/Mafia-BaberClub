# Backend de LA MAFIA BARBER CLUB

Este es el backend de la aplicación de gestión de reservas para LA MAFIA BARBER CLUB, desarrollado con Flask y MySQL.

## Requisitos

- Python 3.8 o superior
- MySQL 8.0 o superior
- pip (gestor de paquetes de Python)

## Instalación

1. Clonar el repositorio:
```bash
git clone <url-del-repositorio>
cd backend
```

2. Crear un entorno virtual:
```bash
python -m venv venv
```

3. Activar el entorno virtual:
- En Windows:
```bash
venv\Scripts\activate
```
- En Linux/Mac:
```bash
source venv/bin/activate
```

4. Instalar las dependencias:
```bash
pip install -r requirements.txt
```

5. Configurar las variables de entorno:
- Crear un archivo `.env` en la carpeta `backend` con el siguiente contenido:
```
# Configuración de la base de datos
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=tu_contraseña
MYSQL_DB=barberia_db

# Configuración de JWT
JWT_SECRET_KEY=tu_clave_secreta_super_segura

# Configuración de la aplicación
SECRET_KEY=clave_secreta_app
DEBUG=True
```

6. Crear la base de datos:
- Importar el archivo `database.sql` en MySQL:
```bash
mysql -u root -p < database.sql
```

## Ejecución

1. Activar el entorno virtual (si no está activado):
```bash
# En Windows
venv\Scripts\activate
# En Linux/Mac
source venv/bin/activate
```

2. Ejecutar la aplicación:
```bash
python app.py
```

La aplicación estará disponible en `http://localhost:5000`

## Endpoints de la API

### Autenticación
- `POST /api/auth/login/barbero` - Login de barberos
- `POST /api/auth/login/cliente` - Login de clientes
- `POST /api/auth/registro/cliente` - Registro de clientes
- `GET /api/auth/perfil` - Obtener perfil del usuario actual

### Barberos
- `GET /api/barberos` - Listar barberos
- `GET /api/barberos/<id>` - Obtener barbero específico
- `GET /api/barberos/horario/<id>` - Obtener horario de un barbero
- `POST /api/barberos/horario` - Crear horario
- `PUT /api/barberos/horario/<id>` - Actualizar horario
- `DELETE /api/barberos/horario/<id>` - Eliminar horario
- `GET /api/barberos/reservas` - Obtener reservas del barbero

### Servicios
- `GET /api/servicios` - Listar servicios
- `GET /api/servicios/<id>` - Obtener servicio específico
- `GET /api/servicios/categorias` - Listar categorías
- `GET /api/servicios/categoria/<id>` - Obtener servicios por categoría
- `POST /api/servicios` - Crear servicio
- `PUT /api/servicios/<id>` - Actualizar servicio
- `DELETE /api/servicios/<id>` - Eliminar servicio

### Reservas
- `GET /api/reservas` - Listar reservas
- `GET /api/reservas/<id>` - Obtener reserva específica
- `POST /api/reservas` - Crear reserva
- `PUT /api/reservas/<id>/estado` - Actualizar estado de reserva
- `PUT /api/reservas/<id>/tiempo` - Actualizar tiempo real de reserva
- `GET /api/reservas/disponibilidad` - Verificar disponibilidad

### Clientes
- `GET /api/clientes/perfil` - Obtener perfil del cliente
- `PUT /api/clientes/perfil` - Actualizar perfil del cliente
- `GET /api/clientes/reservas` - Obtener reservas del cliente
- `GET /api/clientes/reservas/activas` - Obtener reservas activas
- `GET /api/clientes/reservas/historial` - Obtener historial de reservas

## Seguridad

- Todas las contraseñas se almacenan hasheadas usando bcrypt
- Se implementa JWT para la autenticación
- Se verifica la disponibilidad antes de crear reservas
- Se implementa bloqueo de cuenta después de múltiples intentos fallidos de login
- Se validan los datos de entrada en todas las rutas

## Desarrollo

Para contribuir al desarrollo:

1. Crear una rama para tu feature:
```bash
git checkout -b feature/nueva-funcionalidad
```

2. Hacer commit de tus cambios:
```bash
git commit -m 'Agregar nueva funcionalidad'
```

3. Hacer push a la rama:
```bash
git push origin feature/nueva-funcionalidad
```

4. Crear un Pull Request 