import os
import base64

# Generar una clave secreta aleatoria
secret_key = base64.b64encode(os.urandom(32)).decode('utf-8')
print("Tu Secret Key es:")
print(secret_key) 