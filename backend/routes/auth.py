from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import bcrypt
from database import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login/barbero', methods=['POST'])
def login_barbero():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email y contraseña son requeridos'}), 400

    # Verificar si el barbero está bloqueado
    barbero = db.execute_query(
        "SELECT * FROM barberos WHERE bar_email = %s",
        (email,)
    )

    if not barbero:
        return jsonify({'error': 'Credenciales inválidas'}), 401

    barbero = barbero[0]

    if barbero['bar_bloqueado']:
        return jsonify({'error': 'Cuenta bloqueada. Contacte al administrador'}), 403

    # Verificar contraseña
    if not bcrypt.checkpw(password.encode('utf-8'), barbero['bar_password'].encode('utf-8')):
        # Incrementar intentos fallidos
        db.execute_query(
            "UPDATE barberos SET bar_intentos_fallidos = bar_intentos_fallidos + 1 WHERE bar_id = %s",
            (barbero['bar_id'],)
        )
        
        # Bloquear cuenta si hay demasiados intentos fallidos
        if barbero['bar_intentos_fallidos'] >= 4:
            db.execute_query(
                "UPDATE barberos SET bar_bloqueado = TRUE, bar_fecha_bloqueo = CURRENT_TIMESTAMP WHERE bar_id = %s",
                (barbero['bar_id'],)
            )
            return jsonify({'error': 'Cuenta bloqueada por demasiados intentos fallidos'}), 403

        return jsonify({'error': 'Credenciales inválidas'}), 401

    # Resetear intentos fallidos
    db.execute_query(
        "UPDATE barberos SET bar_intentos_fallidos = 0, bar_ultimo_acceso = CURRENT_TIMESTAMP WHERE bar_id = %s",
        (barbero['bar_id'],)
    )

    # Crear token
    access_token = create_access_token(identity={
        'id': barbero['bar_id'],
        'email': barbero['bar_email'],
        'tipo': 'barbero'
    })

    return jsonify({
        'access_token': access_token,
        'barbero': {
            'id': barbero['bar_id'],
            'nombre': barbero['bar_nombre'],
            'email': barbero['bar_email'],
            'especialidad': barbero['bar_especialidad']
        }
    }), 200

@auth_bp.route('/login/cliente', methods=['POST'])
def login_cliente():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email y contraseña son requeridos'}), 400

    cliente = db.execute_query(
        "SELECT * FROM clientes WHERE cli_email = %s",
        (email,)
    )

    if not cliente:
        return jsonify({'error': 'Credenciales inválidas'}), 401

    cliente = cliente[0]

    if not bcrypt.checkpw(password.encode('utf-8'), cliente['cli_password'].encode('utf-8')):
        return jsonify({'error': 'Credenciales inválidas'}), 401

    # Crear token
    access_token = create_access_token(identity={
        'id': cliente['cli_id'],
        'email': cliente['cli_email'],
        'tipo': 'cliente'
    })

    return jsonify({
        'access_token': access_token,
        'cliente': {
            'id': cliente['cli_id'],
            'nombre': cliente['cli_nombre'],
            'email': cliente['cli_email']
        }
    }), 200

@auth_bp.route('/registro/cliente', methods=['POST'])
def registro_cliente():
    data = request.get_json()
    
    # Validar datos requeridos
    required_fields = ['nombre', 'email', 'password', 'telefono']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'El campo {field} es requerido'}), 400

    # Verificar si el email ya existe
    existing_cliente = db.execute_query(
        "SELECT cli_id FROM clientes WHERE cli_email = %s",
        (data['email'],)
    )

    if existing_cliente:
        return jsonify({'error': 'El email ya está registrado'}), 400

    # Hashear contraseña
    hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())

    # Insertar nuevo cliente
    try:
        cliente_id = db.execute_query(
            """
            INSERT INTO clientes (cli_nombre, cli_email, cli_password, cli_telefono)
            VALUES (%s, %s, %s, %s)
            """,
            (data['nombre'], data['email'], hashed_password, data['telefono'])
        )

        # Crear token
        access_token = create_access_token(identity={
            'id': cliente_id,
            'email': data['email'],
            'tipo': 'cliente'
        })

        return jsonify({
            'message': 'Cliente registrado exitosamente',
            'access_token': access_token,
            'cliente': {
                'id': cliente_id,
                'nombre': data['nombre'],
                'email': data['email']
            }
        }), 201

    except Exception as e:
        return jsonify({'error': 'Error al registrar el cliente'}), 500

@auth_bp.route('/perfil', methods=['GET'])
@jwt_required()
def obtener_perfil():
    current_user = get_jwt_identity()
    
    if current_user['tipo'] == 'barbero':
        barbero = db.execute_query(
            "SELECT bar_id, bar_nombre, bar_email, bar_especialidad FROM barberos WHERE bar_id = %s",
            (current_user['id'],)
        )
        if not barbero:
            return jsonify({'error': 'Barbero no encontrado'}), 404
        return jsonify(barbero[0]), 200
    
    else:  # cliente
        cliente = db.execute_query(
            "SELECT cli_id, cli_nombre, cli_email, cli_telefono FROM clientes WHERE cli_id = %s",
            (current_user['id'],)
        )
        if not cliente:
            return jsonify({'error': 'Cliente no encontrado'}), 404
        return jsonify(cliente[0]), 200 