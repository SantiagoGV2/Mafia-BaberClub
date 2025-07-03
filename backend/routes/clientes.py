from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
import bcrypt

clientes_bp = Blueprint('clientes', __name__)

@clientes_bp.route('/perfil', methods=['GET'])
@jwt_required()
def obtener_perfil():
    current_user = get_jwt_identity()
    if current_user['tipo'] != 'cliente':
        return jsonify({'error': 'No autorizado'}), 403

    try:
        cliente = db.execute_query(
            """
            SELECT cli_id, cli_nombre, cli_email, cli_telefono, cli_fecha_registro
            FROM clientes
            WHERE cli_id = %s
            """,
            (current_user['id'],)
        )
        
        if not cliente:
            return jsonify({'error': 'Cliente no encontrado'}), 404
            
        return jsonify(cliente[0]), 200
    except Exception as e:
        return jsonify({'error': 'Error al obtener el perfil'}), 500

@clientes_bp.route('/perfil', methods=['PUT'])
@jwt_required()
def actualizar_perfil():
    current_user = get_jwt_identity()
    if current_user['tipo'] != 'cliente':
        return jsonify({'error': 'No autorizado'}), 403

    data = request.get_json()
    
    try:
        # Verificar que el cliente existe
        cliente = db.execute_query(
            "SELECT cli_id FROM clientes WHERE cli_id = %s",
            (current_user['id'],)
        )
        
        if not cliente:
            return jsonify({'error': 'Cliente no encontrado'}), 404

        # Actualizar perfil
        update_fields = []
        params = []
        
        if 'nombre' in data:
            update_fields.append("cli_nombre = %s")
            params.append(data['nombre'])
            
        if 'telefono' in data:
            update_fields.append("cli_telefono = %s")
            params.append(data['telefono'])
            
        if 'password' in data:
            hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
            update_fields.append("cli_password = %s")
            params.append(hashed_password)

        if not update_fields:
            return jsonify({'error': 'No hay campos para actualizar'}), 400

        params.append(current_user['id'])
        
        query = f"""
            UPDATE clientes
            SET {', '.join(update_fields)}
            WHERE cli_id = %s
        """
        
        db.execute_query(query, tuple(params))
        
        return jsonify({'message': 'Perfil actualizado exitosamente'}), 200
    except Exception as e:
        return jsonify({'error': 'Error al actualizar el perfil'}), 500



# CREATE - Crear nuevo cliente
@clientes_bp.route('/', methods=['POST'])
def crear_cliente():
    data = request.get_json()
    required_fields = ['nombre', 'email', 'password', 'telefono']
    
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Faltan campos requeridos'}), 400

    try:
        # Verificar si el email ya existe
        cliente_existente = db.execute_query(
            "SELECT cli_id FROM clientes WHERE cli_email = %s",
            (data['email'],)
        )
        
        if cliente_existente:
            return jsonify({'error': 'El email ya está registrado'}), 400

        # Hashear contraseña
        hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
        
        # Crear cliente
        cliente_id = db.execute_query(
            """
            INSERT INTO clientes (cli_nombre, cli_email, cli_password, cli_telefono)
            VALUES (%s, %s, %s, %s)
            """,
            (data['nombre'], data['email'], hashed_password, data['telefono'])
        )
        
        return jsonify({
            'message': 'Cliente creado exitosamente',
            'cliente_id': cliente_id
        }), 201
    except Exception as e:
        return jsonify({'error': 'Error al crear el cliente'}), 500

# READ - Obtener todos los clientes (solo admin)
@clientes_bp.route('/', methods=['GET'])
@jwt_required()
def obtener_clientes():
    current_user = get_jwt_identity()
    if current_user['tipo'] != 'admin':
        return jsonify({'error': 'No autorizado'}), 403

    try:
        clientes = db.execute_query(
            """
            SELECT cli_id, cli_nombre, cli_email, cli_telefono, cli_fecha_registro
            FROM clientes
            ORDER BY cli_fecha_registro DESC
            """
        )
        return jsonify(clientes), 200
    except Exception as e:
        return jsonify({'error': 'Error al obtener los clientes'}), 500

# READ - Obtener cliente específico
@clientes_bp.route('/<int:cliente_id>', methods=['GET'])
@jwt_required()
def obtener_cliente(cliente_id):
    current_user = get_jwt_identity()
    if current_user['tipo'] != 'admin' and current_user['id'] != cliente_id:
        return jsonify({'error': 'No autorizado'}), 403

    try:
        cliente = db.execute_query(
            """
            SELECT cli_id, cli_nombre, cli_email, cli_telefono, cli_fecha_registro
            FROM clientes
            WHERE cli_id = %s
            """,
            (cliente_id,)
        )
        
        if not cliente:
            return jsonify({'error': 'Cliente no encontrado'}), 404
            
        return jsonify(cliente[0]), 200
    except Exception as e:
        return jsonify({'error': 'Error al obtener el cliente'}), 500

# UPDATE - Actualizar cliente
@clientes_bp.route('/<int:cliente_id>', methods=['PUT'])
@jwt_required()
def actualizar_cliente(cliente_id):
    current_user = get_jwt_identity()
    if current_user['tipo'] != 'admin' and current_user['id'] != cliente_id:
        return jsonify({'error': 'No autorizado'}), 403

    data = request.get_json()
    
    try:
        # Verificar que el cliente existe
        cliente = db.execute_query(
            "SELECT cli_id FROM clientes WHERE cli_id = %s",
            (cliente_id,)
        )
        
        if not cliente:
            return jsonify({'error': 'Cliente no encontrado'}), 404

        # Actualizar campos
        update_fields = []
        params = []
        
        if 'nombre' in data:
            update_fields.append("cli_nombre = %s")
            params.append(data['nombre'])
            
        if 'telefono' in data:
            update_fields.append("cli_telefono = %s")
            params.append(data['telefono'])
            
        if 'password' in data:
            hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
            update_fields.append("cli_password = %s")
            params.append(hashed_password)

        if not update_fields:
            return jsonify({'error': 'No hay campos para actualizar'}), 400

        params.append(cliente_id)
        
        query = f"""
            UPDATE clientes
            SET {', '.join(update_fields)}
            WHERE cli_id = %s
        """
        
        db.execute_query(query, tuple(params))
        
        return jsonify({'message': 'Cliente actualizado exitosamente'}), 200
    except Exception as e:
        return jsonify({'error': 'Error al actualizar el cliente'}), 500

# DELETE - Eliminar cliente
@clientes_bp.route('/<int:cliente_id>', methods=['DELETE'])
@jwt_required()
def eliminar_cliente(cliente_id):
    current_user = get_jwt_identity()
    if current_user['tipo'] != 'admin':
        return jsonify({'error': 'No autorizado'}), 403

    try:
        # Verificar que el cliente existe
        cliente = db.execute_query(
            "SELECT cli_id FROM clientes WHERE cli_id = %s",
            (cliente_id,)
        )
        
        if not cliente:
            return jsonify({'error': 'Cliente no encontrado'}), 404

        # Eliminar cliente
        db.execute_query(
            "DELETE FROM clientes WHERE cli_id = %s",
            (cliente_id,)
        )
        
        return jsonify({'message': 'Cliente eliminado exitosamente'}), 200
    except Exception as e:
        return jsonify({'error': 'Error al eliminar el cliente'}), 500 