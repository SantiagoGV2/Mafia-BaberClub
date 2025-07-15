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

# --- Recuperación de contraseña para clientes ---
from flask import current_app
from flask_mail import Message
import random
import string
from datetime import datetime, timedelta

@clientes_bp.route('/recuperar-password', methods=['POST'])
def recuperar_password():
    data = request.get_json()
    email = data.get('email')
    if not email:
        return jsonify({'error': 'Email requerido'}), 400

    cliente = db.execute_query("SELECT * FROM clientes WHERE cli_email = %s", (email,))
    if not cliente:
        # No devolvemos un error 404 para no revelar si un email existe o no
        return jsonify({'message': 'Si tu correo está registrado, recibirás un código de recuperación.'}), 200

    codigo = ''.join(random.choices(string.digits, k=6))
    expiracion = datetime.now() + timedelta(minutes=10)

    db.execute_query(
        "UPDATE clientes SET cli_token_recuperacion = %s, cli_token_expiracion = %s WHERE cli_email = %s",
        (codigo, expiracion, email)
    )

    # --- LÓGICA PARA ENVIAR EL CORREO ---
    try:
        msg = Message("Código de Recuperación de Contraseña - LA MAFIA BARBER CLUB",
                      sender=current_app.config['MAIL_DEFAULT_SENDER'],
                      recipients=[email])
        
        # Puedes usar un diseño HTML más elaborado si quieres
        msg.html = f"""
            <div style="font-family: Arial, sans-serif; text-align: center; color: #333;">
                <h2>Recuperación de Contraseña</h2>
                <p>Hola,</p>
                <p>Has solicitado recuperar tu contraseña. Usa el siguiente código para continuar:</p>
                <p style="font-size: 24px; font-weight: bold; letter-spacing: 5px; background-color: #f2f2f2; padding: 10px 20px; border-radius: 5px; display: inline-block;">
                    {codigo}
                </p>
                <p>Este código expirará en 10 minutos.</p>
                <p>Si no solicitaste esto, puedes ignorar este correo.</p>
                <hr>
                <p style="font-size: 12px; color: #888;">LA MAFIA BARBER CLUB</p>
            </div>
        """
        
        # Usamos la instancia 'mail' de nuestra app para enviar el mensaje
        mail = current_app.extensions.get('mail')
        mail.send(msg)

        return jsonify({'message': 'Código enviado al correo'}), 200

    except Exception as e:
        print(f"Error al enviar correo: {e}")
        return jsonify({'error': 'No se pudo enviar el correo de recuperación.'}), 500

@clientes_bp.route('/verificar-codigo', methods=['POST'])
def verificar_codigo():
    data = request.get_json()
    email = data.get('email')
    codigo = data.get('codigo')
    if not email or not codigo:
        return jsonify({'error': 'Datos incompletos'}), 400

    cliente = db.execute_query(
        "SELECT cli_token_recuperacion, cli_token_expiracion FROM clientes WHERE cli_email = %s", (email,)
    )
    if not cliente:
        return jsonify({'error': 'No existe una cuenta con ese email'}), 404

    cliente = cliente[0]
    if cliente['cli_token_recuperacion'] != codigo:
        return jsonify({'error': 'Código incorrecto'}), 400
    if cliente['cli_token_expiracion'] < datetime.now():
        return jsonify({'error': 'Código expirado'}), 400

    return jsonify({'message': 'Código válido'}), 200

@clientes_bp.route('/nueva-password', methods=['POST'])
def nueva_password():
    data = request.get_json()
    email = data.get('email')
    codigo = data.get('codigo')
    nueva_password = data.get('nuevaPassword')
    if not email or not codigo or not nueva_password:
        return jsonify({'error': 'Datos incompletos'}), 400

    cliente = db.execute_query(
        "SELECT cli_token_recuperacion, cli_token_expiracion FROM clientes WHERE cli_email = %s", (email,)
    )
    if not cliente:
        return jsonify({'error': 'No existe una cuenta con ese email'}), 404

    cliente = cliente[0]
    if cliente['cli_token_recuperacion'] != codigo:
        return jsonify({'error': 'Código incorrecto'}), 400
    if cliente['cli_token_expiracion'] < datetime.now():
        return jsonify({'error': 'Código expirado'}), 400

    hashed_password = bcrypt.hashpw(nueva_password.encode('utf-8'), bcrypt.gensalt())
    db.execute_query(
        "UPDATE clientes SET cli_password = %s, cli_token_recuperacion = NULL, cli_token_expiracion = NULL WHERE cli_email = %s",
        (hashed_password, email)
    )
    return jsonify({'message': 'Contraseña actualizada exitosamente'}), 200 