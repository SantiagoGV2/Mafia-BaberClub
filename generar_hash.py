# archivo: generar_hash.py
import bcrypt

# La contraseña que quieres usar para tus barberos de prueba
password_plano = "123456"
password_bytes = password_plano.encode('utf-8')

# Generar el salt y hashear la contraseña
salt = bcrypt.gensalt()
hash_valido = bcrypt.hashpw(password_bytes, salt)

# Imprimir el hash válido para que lo puedas copiar
print("Copia y pega este hash en tu consulta SQL:")
print(hash_valido.decode('utf-8'))