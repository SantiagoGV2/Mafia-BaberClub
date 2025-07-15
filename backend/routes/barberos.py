from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
import bcrypt

barberos_bp = Blueprint('barberos', __name__)

# CREATE - Crear nuevo barbero (solo admin)
@barberos_bp.route('/', methods=['POST'])
@jwt_required()
def crear_barbero():
    current_user = get_jwt_identity()
    if current_user['tipo'] != 'admin':
        return jsonify({'error': 'No autorizado'}), 403

    data = request.get_json()
    required_fields = ['nombre', 'email', 'password', 'especialidad', 'descripcion']
    
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Faltan campos requeridos'}), 400

    try:
        # Verificar si el email ya existe
        barbero_existente = db.execute_query(
            "SELECT bar_id FROM barberos WHERE bar_email = %s",
            (data['email'],)
        )
        
        if barbero_existente:
            return jsonify({'error': 'El email ya está registrado'}), 400

        # Hashear contraseña
        hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
        
        # Crear barbero
        barbero_id = db.execute_query(
            """
            INSERT INTO barberos (
                bar_nombre, bar_email, bar_password, bar_especialidad,
                bar_descripcion, bar_imagen, bar_estado
            )
            VALUES (%s, %s, %s, %s, %s, %s, 'activo')
            """,
            (data['nombre'], data['email'], hashed_password, data['especialidad'],
             data['descripcion'], data.get('imagen', None))
        )
        
        return jsonify({
            'message': 'Barbero creado exitosamente',
            'barbero_id': barbero_id
        }), 201
    except Exception as e:
        return jsonify({'error': 'Error al crear el barbero'}), 500

# READ - Obtener todos los barberos
@barberos_bp.route('/barberos', methods=['GET'])
def obtener_barberos():
    try:
        barberos = db.execute_query(
            """
            SELECT bar_id, bar_nombre, bar_email, bar_especialidad, 
                   bar_descripcion, bar_imagen, bar_estado
            FROM barberos
            WHERE bar_estado = 'activo'
            ORDER BY bar_nombre
            """
        )
        return jsonify(barberos), 200
    except Exception as e:
        return jsonify({'error': 'Error al obtener los barberos'}), 500

# READ - Obtener barbero específico
@barberos_bp.route('/<int:barbero_id>', methods=['GET'])
def obtener_barbero(barbero_id):
    try:
        barbero = db.execute_query(
            """
            SELECT bar_id, bar_nombre, bar_email, bar_especialidad,
                   bar_descripcion, bar_imagen, bar_estado
            FROM barberos
            WHERE bar_id = %s
            """,
            (barbero_id,)
        )
        
        if not barbero:
            return jsonify({'error': 'Barbero no encontrado'}), 404
            
        return jsonify(barbero[0]), 200
    except Exception as e:
        return jsonify({'error': 'Error al obtener el barbero'}), 500

# UPDATE - Actualizar barbero
@barberos_bp.route('/<int:barbero_id>', methods=['PUT'])
@jwt_required()
def actualizar_barbero(barbero_id):
    current_user = get_jwt_identity()
    if current_user['tipo'] != 'admin' and current_user['id'] != barbero_id:
        return jsonify({'error': 'No autorizado'}), 403

    data = request.get_json()
    
    try:
        # Verificar que el barbero existe
        barbero = db.execute_query(
            "SELECT bar_id FROM barberos WHERE bar_id = %s",
            (barbero_id,)
        )
        
        if not barbero:
            return jsonify({'error': 'Barbero no encontrado'}), 404

        # Actualizar campos
        update_fields = []
        params = []
        
        if 'nombre' in data:
            update_fields.append("bar_nombre = %s")
            params.append(data['nombre'])
            
        if 'especialidad' in data:
            update_fields.append("bar_especialidad = %s")
            params.append(data['especialidad'])
            
        if 'descripcion' in data:
            update_fields.append("bar_descripcion = %s")
            params.append(data['descripcion'])
            
        if 'imagen' in data:
            update_fields.append("bar_imagen = %s")
            params.append(data['imagen'])
            
        if 'estado' in data:
            update_fields.append("bar_estado = %s")
            params.append(data['estado'])
            
        if 'password' in data:
            hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
            update_fields.append("bar_password = %s")
            params.append(hashed_password)

        if not update_fields:
            return jsonify({'error': 'No hay campos para actualizar'}), 400

        params.append(barbero_id)
        
        query = f"""
            UPDATE barberos
            SET {', '.join(update_fields)}
            WHERE bar_id = %s
        """
        
        db.execute_query(query, tuple(params))
        
        return jsonify({'message': 'Barbero actualizado exitosamente'}), 200
    except Exception as e:
        return jsonify({'error': 'Error al actualizar el barbero'}), 500

# DELETE - Eliminar barbero (marcar como inactivo)
@barberos_bp.route('/<int:barbero_id>', methods=['DELETE'])
@jwt_required()
def eliminar_barbero(barbero_id):
    current_user = get_jwt_identity()
    if current_user['tipo'] != 'admin':
        return jsonify({'error': 'No autorizado'}), 403

    try:
        # Verificar que el barbero existe
        barbero = db.execute_query(
            "SELECT bar_id FROM barberos WHERE bar_id = %s",
            (barbero_id,)
        )
        
        if not barbero:
            return jsonify({'error': 'Barbero no encontrado'}), 404

        # Marcar barbero como inactivo
        db.execute_query(
            "UPDATE barberos SET bar_estado = 'inactivo' WHERE bar_id = %s",
            (barbero_id,)
        )
        
        return jsonify({'message': 'Barbero eliminado exitosamente'}), 200
    except Exception as e:
        return jsonify({'error': 'Error al eliminar el barbero'}), 500

@barberos_bp.route('/horario/<int:barbero_id>', methods=['GET'])
def obtener_horario_barbero(barbero_id):
    try:
        horario = db.execute_query(
            """
            SELECT hor_id, hor_dia_semana, hor_hora_inicio, hor_hora_fin
            FROM horarios_barberos
            WHERE hor_barbero_id = %s
            ORDER BY FIELD(hor_dia_semana, 'lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo')
            """,
            (barbero_id,)
        )
        return jsonify(horario), 200
    except Exception as e:
        return jsonify({'error': 'Error al obtener el horario del barbero'}), 500

@barberos_bp.route('/horario', methods=['POST'])
@jwt_required()
def crear_horario():
    current_user = get_jwt_identity()
    if current_user['tipo'] != 'barbero':
        return jsonify({'error': 'No autorizado'}), 403

    data = request.get_json()
    required_fields = ['dia_semana', 'hora_inicio', 'hora_fin']
    
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'El campo {field} es requerido'}), 400

    try:
        horario_id = db.execute_query(
            """
            INSERT INTO horarios_barberos (hor_barbero_id, hor_dia_semana, hor_hora_inicio, hor_hora_fin)
            VALUES (%s, %s, %s, %s)
            """,
            (current_user['id'], data['dia_semana'], data['hora_inicio'], data['hora_fin'])
        )
        
        return jsonify({
            'message': 'Horario creado exitosamente',
            'horario_id': horario_id
        }), 201
    except Exception as e:
        return jsonify({'error': 'Error al crear el horario'}), 500

@barberos_bp.route('/horario/<int:horario_id>', methods=['PUT'])
@jwt_required()
def actualizar_horario(horario_id):
    current_user = get_jwt_identity()
    if current_user['tipo'] != 'barbero':
        return jsonify({'error': 'No autorizado'}), 403

    data = request.get_json()
    
    try:
        # Verificar que el horario pertenece al barbero
        horario = db.execute_query(
            "SELECT hor_id FROM horarios_barberos WHERE hor_id = %s AND hor_barbero_id = %s",
            (horario_id, current_user['id'])
        )
        
        if not horario:
            return jsonify({'error': 'Horario no encontrado'}), 404

        # Actualizar horario
        db.execute_query(
            """
            UPDATE horarios_barberos
            SET hor_dia_semana = %s, hor_hora_inicio = %s, hor_hora_fin = %s
            WHERE hor_id = %s
            """,
            (data['dia_semana'], data['hora_inicio'], data['hora_fin'], horario_id)
        )
        
        return jsonify({'message': 'Horario actualizado exitosamente'}), 200
    except Exception as e:
        return jsonify({'error': 'Error al actualizar el horario'}), 500

@barberos_bp.route('/horario/<int:horario_id>', methods=['DELETE'])
@jwt_required()
def eliminar_horario(horario_id):
    current_user = get_jwt_identity()
    if current_user['tipo'] != 'barbero':
        return jsonify({'error': 'No autorizado'}), 403

    try:
        # Verificar que el horario pertenece al barbero
        horario = db.execute_query(
            "SELECT hor_id FROM horarios_barberos WHERE hor_id = %s AND hor_barbero_id = %s",
            (horario_id, current_user['id'])
        )
        
        if not horario:
            return jsonify({'error': 'Horario no encontrado'}), 404

        # Eliminar horario
        db.execute_query(
            "DELETE FROM horarios_barberos WHERE hor_id = %s",
            (horario_id,)
        )
        
        return jsonify({'message': 'Horario eliminado exitosamente'}), 200
    except Exception as e:
        return jsonify({'error': 'Error al eliminar el horario'}), 500

@barberos_bp.route('/reservas', methods=['GET'])
@jwt_required()
def obtener_reservas_barbero():
    current_user = get_jwt_identity()
    if current_user['tipo'] != 'barbero':
        return jsonify({'error': 'No autorizado'}), 403

    try:
        reservas = db.execute_query(
            """
            SELECT r.*, c.cli_nombre, c.cli_telefono, s.ser_nombre
            FROM reservas r
            JOIN clientes c ON r.res_cliente_id = c.cli_id
            JOIN servicios s ON r.res_servicio_id = s.ser_id
            WHERE r.res_barbero_id = %s
            ORDER BY r.res_fecha DESC, r.res_hora_inicio DESC
            """,
            (current_user['id'],)
        )
        return jsonify(reservas), 200
    except Exception as e:
        return jsonify({'error': 'Error al obtener las reservas'}), 500 

# --- Recuperación de contraseña para barberos ---
from flask import current_app
import random
import string
from datetime import datetime, timedelta

@barberos_bp.route('/recuperar-password', methods=['POST'])
def recuperar_password_barbero():
    data = request.get_json()
    email = data.get('email')
    if not email:
        return jsonify({'error': 'Email requerido'}), 400

    barbero = db.execute_query("SELECT * FROM barberos WHERE bar_email = %s", (email,))
    if not barbero:
        return jsonify({'error': 'No existe una cuenta con ese email'}), 404

    codigo = ''.join(random.choices(string.digits, k=6))
    expiracion = datetime.now() + timedelta(minutes=10)

    db.execute_query(
        "UPDATE barberos SET bar_token_recuperacion = %s, bar_token_expiracion = %s WHERE bar_email = %s",
        (codigo, expiracion, email)
    )

    print(f"Código de recuperación para barbero {email}: {codigo}")
    return jsonify({'message': 'Código enviado al correo'}), 200

@barberos_bp.route('/verificar-codigo', methods=['POST'])
def verificar_codigo_barbero():
    data = request.get_json()
    email = data.get('email')
    codigo = data.get('codigo')
    if not email or not codigo:
        return jsonify({'error': 'Datos incompletos'}), 400

    barbero = db.execute_query(
        "SELECT bar_token_recuperacion, bar_token_expiracion FROM barberos WHERE bar_email = %s", (email,)
    )
    if not barbero:
        return jsonify({'error': 'No existe una cuenta con ese email'}), 404

    barbero = barbero[0]
    if barbero['bar_token_recuperacion'] != codigo:
        return jsonify({'error': 'Código incorrecto'}), 400
    if barbero['bar_token_expiracion'] < datetime.now():
        return jsonify({'error': 'Código expirado'}), 400

    return jsonify({'message': 'Código válido'}), 200

@barberos_bp.route('/nueva-password', methods=['POST'])
def nueva_password_barbero():
    data = request.get_json()
    email = data.get('email')
    codigo = data.get('codigo')
    nueva_password = data.get('nuevaPassword')
    if not email or not codigo or not nueva_password:
        return jsonify({'error': 'Datos incompletos'}), 400

    barbero = db.execute_query(
        "SELECT bar_token_recuperacion, bar_token_expiracion FROM barberos WHERE bar_email = %s", (email,)
    )
    if not barbero:
        return jsonify({'error': 'No existe una cuenta con ese email'}), 404

    barbero = barbero[0]
    if barbero['bar_token_recuperacion'] != codigo:
        return jsonify({'error': 'Código incorrecto'}), 400
    if barbero['bar_token_expiracion'] < datetime.now():
        return jsonify({'error': 'Código expirado'}), 400

    hashed_password = bcrypt.hashpw(nueva_password.encode('utf-8'), bcrypt.gensalt())
    db.execute_query(
        "UPDATE barberos SET bar_password = %s, bar_token_recuperacion = NULL, bar_token_expiracion = NULL WHERE bar_email = %s",
        (hashed_password, email)
    )
    return jsonify({'message': 'Contraseña actualizada exitosamente'}), 200 