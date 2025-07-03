from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db

servicios_bp = Blueprint('servicios', __name__)

@servicios_bp.route('/', methods=['GET'])
def obtener_servicios():
    try:
        servicios = db.execute_query(
            """
            SELECT s.*, c.cat_nombre as categoria_nombre
            FROM servicios s
            JOIN categorias_servicios c ON s.ser_categoria_id = c.cat_id
            WHERE s.ser_estado = 'activo'
            ORDER BY c.cat_nombre, s.ser_nombre
            """
        )
        return jsonify(servicios), 200
    except Exception as e:
        return jsonify({'error': 'Error al obtener los servicios'}), 500

@servicios_bp.route('/<int:servicio_id>', methods=['GET'])
def obtener_servicio(servicio_id):
    try:
        servicio = db.execute_query(
            """
            SELECT s.*, c.cat_nombre as categoria_nombre
            FROM servicios s
            JOIN categorias_servicios c ON s.ser_categoria_id = c.cat_id
            WHERE s.ser_id = %s
            """,
            (servicio_id,)
        )
        
        if not servicio:
            return jsonify({'error': 'Servicio no encontrado'}), 404
            
        return jsonify(servicio[0]), 200
    except Exception as e:
        return jsonify({'error': 'Error al obtener el servicio'}), 500

@servicios_bp.route('/categorias', methods=['GET'])
def obtener_categorias():
    try:
        categorias = db.execute_query(
            "SELECT * FROM categorias_servicios ORDER BY cat_nombre"
        )
        return jsonify(categorias), 200
    except Exception as e:
        return jsonify({'error': 'Error al obtener las categorías'}), 500

@servicios_bp.route('/categoria/<int:categoria_id>', methods=['GET'])
def obtener_servicios_por_categoria(categoria_id):
    try:
        servicios = db.execute_query(
            """
            SELECT s.*, c.cat_nombre as categoria_nombre
            FROM servicios s
            JOIN categorias_servicios c ON s.ser_categoria_id = c.cat_id
            WHERE s.ser_categoria_id = %s AND s.ser_estado = 'activo'
            ORDER BY s.ser_nombre
            """,
            (categoria_id,)
        )
        return jsonify(servicios), 200
    except Exception as e:
        return jsonify({'error': 'Error al obtener los servicios de la categoría'}), 500

@servicios_bp.route('/', methods=['POST'])
@jwt_required()
def crear_servicio():
    current_user = get_jwt_identity()
    if current_user['tipo'] != 'admin':
        return jsonify({'error': 'No autorizado'}), 403

    data = request.get_json()
    required_fields = ['nombre', 'descripcion', 'duracion', 'precio', 'categoria_id']
    
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Faltan campos requeridos'}), 400

    try:
        # Verificar que la categoría existe
        categoria = db.execute_query(
            "SELECT cat_id FROM categorias_servicios WHERE cat_id = %s",
            (data['categoria_id'],)
        )
        
        if not categoria:
            return jsonify({'error': 'Categoría no encontrada'}), 404

        # Crear servicio
        servicio_id = db.execute_query(
            """
            INSERT INTO servicios (
                ser_nombre, ser_descripcion, ser_duracion,
                ser_precio, ser_categoria_id, ser_estado
            )
            VALUES (%s, %s, %s, %s, %s, 'activo')
            """,
            (data['nombre'], data['descripcion'], data['duracion'],
             data['precio'], data['categoria_id'])
        )
        
        return jsonify({
            'message': 'Servicio creado exitosamente',
            'servicio_id': servicio_id
        }), 201
    except Exception as e:
        return jsonify({'error': 'Error al crear el servicio'}), 500

@servicios_bp.route('/<int:servicio_id>', methods=['PUT'])
@jwt_required()
def actualizar_servicio(servicio_id):
    current_user = get_jwt_identity()
    if current_user['tipo'] != 'admin':
        return jsonify({'error': 'No autorizado'}), 403

    data = request.get_json()
    
    try:
        # Verificar que el servicio existe
        servicio = db.execute_query(
            "SELECT ser_id FROM servicios WHERE ser_id = %s",
            (servicio_id,)
        )
        
        if not servicio:
            return jsonify({'error': 'Servicio no encontrado'}), 404

        # Verificar que la categoría existe si se proporciona
        if 'categoria_id' in data:
            categoria = db.execute_query(
                "SELECT cat_id FROM categorias_servicios WHERE cat_id = %s",
                (data['categoria_id'],)
            )
            
            if not categoria:
                return jsonify({'error': 'Categoría no encontrada'}), 404

        # Actualizar campos
        update_fields = []
        params = []
        
        if 'nombre' in data:
            update_fields.append("ser_nombre = %s")
            params.append(data['nombre'])
            
        if 'descripcion' in data:
            update_fields.append("ser_descripcion = %s")
            params.append(data['descripcion'])
            
        if 'duracion' in data:
            update_fields.append("ser_duracion = %s")
            params.append(data['duracion'])
            
        if 'precio' in data:
            update_fields.append("ser_precio = %s")
            params.append(data['precio'])
            
        if 'categoria_id' in data:
            update_fields.append("ser_categoria_id = %s")
            params.append(data['categoria_id'])
            
        if 'estado' in data:
            update_fields.append("ser_estado = %s")
            params.append(data['estado'])

        if not update_fields:
            return jsonify({'error': 'No hay campos para actualizar'}), 400

        params.append(servicio_id)
        
        query = f"""
            UPDATE servicios
            SET {', '.join(update_fields)}
            WHERE ser_id = %s
        """
        
        db.execute_query(query, tuple(params))
        
        return jsonify({'message': 'Servicio actualizado exitosamente'}), 200
    except Exception as e:
        return jsonify({'error': 'Error al actualizar el servicio'}), 500

@servicios_bp.route('/<int:servicio_id>', methods=['DELETE'])
@jwt_required()
def eliminar_servicio(servicio_id):
    current_user = get_jwt_identity()
    if current_user['tipo'] != 'admin':
        return jsonify({'error': 'No autorizado'}), 403

    try:
        # Verificar que el servicio existe
        servicio = db.execute_query(
            "SELECT ser_id FROM servicios WHERE ser_id = %s",
            (servicio_id,)
        )
        
        if not servicio:
            return jsonify({'error': 'Servicio no encontrado'}), 404

        # Marcar servicio como inactivo
        db.execute_query(
            "UPDATE servicios SET ser_estado = 'inactivo' WHERE ser_id = %s",
            (servicio_id,)
        )
        
        return jsonify({'message': 'Servicio eliminado exitosamente'}), 200
    except Exception as e:
        return jsonify({'error': 'Error al eliminar el servicio'}), 500 