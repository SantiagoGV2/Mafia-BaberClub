from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
from datetime import datetime, timedelta

reservas_bp = Blueprint('reservas', __name__)

@reservas_bp.route('/', methods=['GET'])
@jwt_required()
def obtener_reservas():
    current_user = get_jwt_identity()
    
    try:
        if current_user['tipo'] == 'barbero':
            # Obtener reservas del barbero
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
        elif current_user['tipo'] == 'cliente':
            # --- CORRECCIÓN AQUÍ ---
            # Reemplazamos 'r.*' por una selección explícita y formateada
            sql_query = """
                SELECT 
                    r.res_id,
                    CAST(r.res_fecha AS CHAR) as res_fecha,
                    CONCAT(LPAD(HOUR(r.res_hora_inicio), 2, '0'), ':', LPAD(MINUTE(r.res_hora_inicio), 2, '0')) as res_hora_inicio,
                    r.res_estado,
                    CAST(r.res_total_pagar AS CHAR) as res_total_pagar,
                    r.res_notas,
                    b.bar_nombre, 
                    s.ser_nombre
                FROM reservas r
                JOIN barberos b ON r.res_barbero_id = b.bar_id
                JOIN servicios s ON r.res_servicio_id = s.ser_id
                WHERE r.res_cliente_id = %s
                ORDER BY r.res_fecha DESC, r.res_hora_inicio DESC
            """
            reservas = db.execute_query(sql_query, (current_user['id'],))
        else:  # admin
            # Obtener todas las reservas
            reservas = db.execute_query(
                """
                SELECT r.*, c.cli_nombre, b.bar_nombre, s.ser_nombre
                FROM reservas r
                JOIN clientes c ON r.res_cliente_id = c.cli_id
                JOIN barberos b ON r.res_barbero_id = b.bar_id
                JOIN servicios s ON r.res_servicio_id = s.ser_id
                ORDER BY r.res_fecha DESC, r.res_hora_inicio DESC
                """
            )
        
        return jsonify(reservas), 200
    except Exception as e:
        return jsonify({'error': 'Error al obtener las reservas'}), 500

@reservas_bp.route('/<int:reserva_id>', methods=['GET'])
@jwt_required()
def obtener_reserva(reserva_id):
    current_user = get_jwt_identity()
    
    # Creamos la consulta base que formatea todos los datos
    sql_query = """
        SELECT 
            r.res_id,
            CAST(r.res_fecha AS CHAR) as res_fecha,
            CONCAT(LPAD(HOUR(r.res_hora_inicio), 2, '0'), ':', LPAD(MINUTE(r.res_hora_inicio), 2, '0')) as res_hora_inicio,
            CONCAT(LPAD(HOUR(r.res_hora_fin), 2, '0'), ':', LPAD(MINUTE(r.res_hora_fin), 2, '0')) as res_hora_fin,
            r.res_estado,
            CAST(r.res_total_pagar AS CHAR) as res_total_pagar,
            r.res_notas,
            s.ser_nombre, 
            b.bar_nombre,
            c.cli_nombre,
            c.cli_telefono
        FROM reservas r
        JOIN barberos b ON r.res_barbero_id = b.bar_id
        JOIN servicios s ON r.res_servicio_id = s.ser_id
        JOIN clientes c ON r.res_cliente_id = c.cli_id
        WHERE r.res_id = %s
    """
    params = [reserva_id]

    try:
        # Añadimos condiciones de seguridad según el tipo de usuario
        if current_user['tipo'] == 'cliente':
            sql_query += " AND r.res_cliente_id = %s"
            params.append(current_user['id'])
        elif current_user['tipo'] == 'barbero':
            sql_query += " AND r.res_barbero_id = %s"
            params.append(current_user['id'])
        
        # El admin no necesita filtros adicionales
        
        reserva = db.execute_query(sql_query, tuple(params))
        
        if not reserva:
            return jsonify({'error': 'Reserva no encontrada o no tienes permiso para verla'}), 404
            
        return jsonify(reserva[0]), 200
        
    except Exception as e:
        print(f"Error al obtener detalle de reserva: {e}")
        return jsonify({'error': 'Error al obtener la reserva'}), 500

@reservas_bp.route('/', methods=['POST'])
@jwt_required()
def crear_reserva():
    current_user = get_jwt_identity()
    if current_user['tipo'] != 'cliente':
        return jsonify({'error': 'Solo los clientes pueden crear reservas'}), 403

    data = request.get_json()
    required_fields = ['barbero_id', 'servicio_id', 'fecha', 'hora_inicio']
    
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Faltan campos requeridos'}), 400

    try:
        # Esta parte ya funciona bien. La reserva se crea.
        reserva_id = db.execute_query(
            """
            INSERT INTO reservas (
                res_cliente_id, res_servicio_id, res_barbero_id,
                res_fecha, res_hora_inicio, res_notas
            ) VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                current_user['id'], data['servicio_id'], data['barbero_id'],
                data['fecha'], data['hora_inicio'],
                data.get('notas', None)
            )
        )

        # --- CORRECCIÓN FINAL AQUÍ ---
        # Reescribimos la consulta SELECT para que sea a prueba de errores.
        nueva_reserva = db.execute_query(
            """
            SELECT 
                r.res_id,
                CAST(r.res_fecha AS CHAR) as res_fecha,
                CONCAT(LPAD(HOUR(r.res_hora_inicio), 2, '0'), ':', LPAD(MINUTE(r.res_hora_inicio), 2, '0'), ':', LPAD(SECOND(r.res_hora_inicio), 2, '0')) as res_hora_inicio,
                CONCAT(LPAD(HOUR(r.res_hora_fin), 2, '0'), ':', LPAD(MINUTE(r.res_hora_fin), 2, '0'), ':', LPAD(SECOND(r.res_hora_fin), 2, '0')) as res_hora_fin,
                r.res_estado,
                CAST(r.res_total_pagar AS CHAR) as res_total_pagar,
                r.res_notas,
                s.ser_nombre, 
                b.bar_nombre, 
                c.cli_nombre
            FROM reservas r
            JOIN servicios s ON r.res_servicio_id = s.ser_id
            JOIN barberos b ON r.res_barbero_id = b.bar_id
            JOIN clientes c ON r.res_cliente_id = c.cli_id
            WHERE r.res_id = %s
            """,
            (reserva_id,)
        )

        if nueva_reserva:
            return jsonify(nueva_reserva[0]), 201
        else:
            return jsonify({'error': 'No se pudo encontrar la reserva recién creada'}), 404

    except Exception as e:
        if 'El barbero no está disponible en ese horario' in str(e):
            return jsonify({'error': 'El barbero no está disponible en ese horario'}), 409
        
        print(f"Error al crear reserva: {e}")
        return jsonify({'error': 'Ocurrió un error al procesar la reserva.'}), 500

@reservas_bp.route('/<int:reserva_id>/estado', methods=['PUT'])
@jwt_required()
def actualizar_estado_reserva(reserva_id):
    current_user = get_jwt_identity()
    if current_user['tipo'] != 'barbero':
        return jsonify({'error': 'No autorizado'}), 403

    data = request.get_json()
    if 'estado' not in data:
        return jsonify({'error': 'El estado es requerido'}), 400

    try:
        # Verificar que la reserva existe y pertenece al barbero
        reserva = db.execute_query(
            "SELECT res_id FROM reservas WHERE res_id = %s AND res_barbero_id = %s",
            (reserva_id, current_user['id'])
        )
        
        if not reserva:
            return jsonify({'error': 'Reserva no encontrada'}), 404

        # Actualizar estado
        db.execute_query(
            """
            UPDATE reservas
            SET res_estado = %s,
                res_fecha_completado = CASE
                    WHEN %s = 'completada' THEN CURRENT_TIMESTAMP
                    ELSE res_fecha_completado
                END
            WHERE res_id = %s
            """,
            (data['estado'], data['estado'], reserva_id)
        )
        
        return jsonify({'message': 'Estado de la reserva actualizado exitosamente'}), 200
    except Exception as e:
        return jsonify({'error': 'Error al actualizar el estado de la reserva'}), 500

@reservas_bp.route('/<int:reserva_id>/tiempo', methods=['PUT'])
@jwt_required()
def actualizar_tiempo_reserva(reserva_id):
    current_user = get_jwt_identity()
    if current_user['tipo'] != 'barbero':
        return jsonify({'error': 'No autorizado'}), 403

    data = request.get_json()
    if 'tiempo_real_duracion' not in data:
        return jsonify({'error': 'El tiempo real de duración es requerido'}), 400

    try:
        # Verificar que la reserva existe y pertenece al barbero
        reserva = db.execute_query(
            "SELECT res_id FROM reservas WHERE res_id = %s AND res_barbero_id = %s",
            (reserva_id, current_user['id'])
        )
        
        if not reserva:
            return jsonify({'error': 'Reserva no encontrada'}), 404

        # Actualizar tiempo real
        db.execute_query(
            """
            UPDATE reservas
            SET res_tiempo_real_duracion = %s
            WHERE res_id = %s
            """,
            (data['tiempo_real_duracion'], reserva_id)
        )
        
        return jsonify({'message': 'Tiempo real de la reserva actualizado exitosamente'}), 200
    except Exception as e:
        return jsonify({'error': 'Error al actualizar el tiempo real de la reserva'}), 500

@reservas_bp.route('/disponibilidad', methods=['GET'])
def verificar_disponibilidad():
    barbero_id = request.args.get('barbero_id')
    fecha = request.args.get('fecha')
    
    if not barbero_id or not fecha:
        return jsonify({'error': 'Barbero y fecha son requeridos'}), 400

    try:
        # --- SOLUCIÓN NUCLEAR: Eliminamos TIME_FORMAT por completo ---
        # Construimos la hora manualmente para evitar cualquier conflicto con '%'
        horario_db = db.execute_query(
            """
            SELECT 
                hor_dia_semana, 
                CONCAT(
                    LPAD(HOUR(hor_hora_inicio), 2, '0'), ':',
                    LPAD(MINUTE(hor_hora_inicio), 2, '0'), ':',
                    LPAD(SECOND(hor_hora_inicio), 2, '0')
                ) as hor_hora_inicio,
                CONCAT(
                    LPAD(HOUR(hor_hora_fin), 2, '0'), ':',
                    LPAD(MINUTE(hor_hora_fin), 2, '0'), ':',
                    LPAD(SECOND(hor_hora_fin), 2, '0')
                ) as hor_hora_fin
            FROM horarios_barberos
            WHERE hor_barbero_id = %s
            """,
            (barbero_id,)
        )
        
        reservas_db = db.execute_query(
            """
            SELECT 
                CONCAT(
                    LPAD(HOUR(res_hora_inicio), 2, '0'), ':',
                    LPAD(MINUTE(res_hora_inicio), 2, '0'), ':',
                    LPAD(SECOND(res_hora_inicio), 2, '0')
                ) as res_hora_inicio,
                CONCAT(
                    LPAD(HOUR(res_hora_fin), 2, '0'), ':',
                    LPAD(MINUTE(res_hora_fin), 2, '0'), ':',
                    LPAD(SECOND(res_hora_fin), 2, '0')
                ) as res_hora_fin
            FROM reservas
            WHERE res_barbero_id = %s
            AND res_fecha = %s
            AND res_estado != 'cancelada'
            """,
            (barbero_id, fecha)
        )
        
        servicios_db = db.execute_query(
            "SELECT ser_id, ser_nombre, ser_duracion, ser_precio FROM servicios WHERE ser_estado = 'activo' ORDER BY ser_nombre"
        )
        
        servicios_serializables = [
            {
                "ser_id": s["ser_id"],
                "ser_nombre": s["ser_nombre"],
                "ser_duracion": s["ser_duracion"],
                "ser_precio": str(s["ser_precio"])
            } for s in servicios_db
        ]
        
        return jsonify({
            'horario': horario_db,
            'reservas': reservas_db,
            'servicios': servicios_serializables
        }), 200

    except Exception as e:
        print(f"Error detallado en /disponibilidad: {e}")
        return jsonify({'error': 'Error interno del servidor.'}), 500

@reservas_bp.route('/<int:reserva_id>/modificar', methods=['PUT'])
@jwt_required()
def modificar_reserva(reserva_id):
    current_user = get_jwt_identity()
    if current_user['tipo'] not in ['admin', 'barbero']:
        return jsonify({'error': 'No autorizado'}), 403

    data = request.get_json()
    
    try:
        # Verificar que la reserva existe
        reserva = db.execute_query(
            """
            SELECT r.*, b.bar_id as barbero_id
            FROM reservas r
            JOIN barberos b ON r.res_barbero_id = b.bar_id
            WHERE r.res_id = %s
            """,
            (reserva_id,)
        )
        
        if not reserva:
            return jsonify({'error': 'Reserva no encontrada'}), 404

        reserva = reserva[0]
        
        # Verificar permisos
        if current_user['tipo'] == 'barbero' and current_user['id'] != reserva['barbero_id']:
            return jsonify({'error': 'No autorizado'}), 403

        # Verificar disponibilidad si se cambia la fecha/hora
        if 'fecha' in data or 'hora_inicio' in data:
            fecha = data.get('fecha', reserva['res_fecha'])
            hora_inicio = data.get('hora_inicio', reserva['res_hora_inicio'])
            
            reservas_existentes = db.execute_query(
                """
                SELECT COUNT(*) as count
                FROM reservas
                WHERE res_barbero_id = %s
                AND res_fecha = %s
                AND res_id != %s
                AND res_estado != 'cancelada'
                AND (
                    (res_hora_inicio <= %s AND res_hora_fin > %s)
                    OR (res_hora_inicio < %s AND res_hora_fin >= %s)
                    OR (res_hora_inicio >= %s AND res_hora_fin <= %s)
                )
                """,
                (reserva['barbero_id'], fecha, reserva_id,
                 hora_inicio, hora_inicio, hora_inicio, hora_inicio,
                 hora_inicio, hora_inicio)
            )

            if reservas_existentes[0]['count'] > 0:
                return jsonify({'error': 'El barbero no está disponible en ese horario'}), 400

        # Actualizar campos
        update_fields = []
        params = []
        
        if 'servicio_id' in data:
            update_fields.append("res_servicio_id = %s")
            params.append(data['servicio_id'])
            
        if 'fecha' in data:
            update_fields.append("res_fecha = %s")
            params.append(data['fecha'])
            
        if 'hora_inicio' in data:
            update_fields.append("res_hora_inicio = %s")
            params.append(data['hora_inicio'])
            
        if 'estado' in data:
            update_fields.append("res_estado = %s")
            params.append(data['estado'])
            
        if 'notas' in data:
            update_fields.append("res_notas = %s")
            params.append(data['notas'])

        if not update_fields:
            return jsonify({'error': 'No hay campos para actualizar'}), 400

        params.append(reserva_id)
        
        query = f"""
            UPDATE reservas
            SET {', '.join(update_fields)}
            WHERE res_id = %s
        """
        
        db.execute_query(query, tuple(params))
        
        # Obtener la reserva actualizada
        reserva_actualizada = db.execute_query(
            """
            SELECT r.*, s.ser_nombre, b.bar_nombre
            FROM reservas r
            JOIN servicios s ON r.res_servicio_id = s.ser_id
            JOIN barberos b ON r.res_barbero_id = b.bar_id
            WHERE r.res_id = %s
            """,
            (reserva_id,)
        )

        return jsonify(reserva_actualizada[0]), 200
    except Exception as e:
        return jsonify({'error': 'Error al actualizar la reserva'}), 500

@reservas_bp.route('/<int:reserva_id>/eliminar', methods=['DELETE'])
@jwt_required()
def eliminar_reserva(reserva_id):
    current_user = get_jwt_identity()
    
    try:
        # Verificar que la reserva existe
        reserva = db.execute_query(
            """
            SELECT r.*, c.cli_id as cliente_id, b.bar_id as barbero_id
            FROM reservas r
            JOIN clientes c ON r.res_cliente_id = c.cli_id
            JOIN barberos b ON r.res_barbero_id = b.bar_id
            WHERE r.res_id = %s
            """,
            (reserva_id,)
        )
        
        if not reserva:
            return jsonify({'error': 'Reserva no encontrada'}), 404

        reserva = reserva[0]
        
        # Verificar permisos
        if current_user['tipo'] == 'cliente' and current_user['id'] != reserva['cliente_id']:
            return jsonify({'error': 'No autorizado'}), 403
        elif current_user['tipo'] == 'barbero' and current_user['id'] != reserva['barbero_id']:
            return jsonify({'error': 'No autorizado'}), 403
        elif current_user['tipo'] not in ['admin', 'cliente', 'barbero']:
            return jsonify({'error': 'No autorizado'}), 403

        # Marcar reserva como cancelada
        db.execute_query(
            "UPDATE reservas SET res_estado = 'cancelada' WHERE res_id = %s",
            (reserva_id,)
        )
        
        return jsonify({'message': 'Reserva cancelada exitosamente'}), 200
    except Exception as e:
        return jsonify({'error': 'Error al cancelar la reserva'}), 500 
    
@reservas_bp.route('/<int:reserva_id>/cancelar', methods=['PUT'])
@jwt_required()
def cancelar_reserva_cliente(reserva_id):
    current_user = get_jwt_identity()
    if current_user.get('tipo') != 'cliente':
        return jsonify(message="Acceso no autorizado."), 403

    try:
        # Primero, verifica que la reserva exista y pertenezca al cliente.
        reserva = db.execute_query(
            "SELECT res_id, res_estado FROM reservas WHERE res_id = %s AND res_cliente_id = %s",
            (reserva_id, current_user['id'])
        )
        if not reserva:
            return jsonify(message="Reserva no encontrada o no te pertenece."), 404

        # Opcional: Permitir cancelar solo si está 'pendiente' o 'confirmada'
        if reserva[0]['res_estado'] not in ['pendiente', 'confirmada']:
            return jsonify(message=f"No puedes cancelar una reserva que ya está '{reserva[0]['res_estado']}'."), 400

        # Actualiza el estado a 'cancelada'
        db.execute_query(
            "UPDATE reservas SET res_estado = 'cancelada' WHERE res_id = %s",
            (reserva_id,)
        )
        return jsonify(message="Reserva cancelada exitosamente."), 200

    except Exception as e:
        print(f"Error al cancelar reserva: {e}")
        return jsonify(message="Error interno al cancelar la reserva."), 500