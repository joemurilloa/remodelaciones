from flask import Flask, Response
import json

# Crear la aplicación Flask
app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return {'message': 'API funcionando correctamente'}

@app.route('/api/cotizacion', methods=['POST'])
def cotizacion():
    try:
        return {'message': 'Endpoint de cotización'}
    except Exception as e:
        return {'error': str(e)}, 500

def handler(event, context):
    """Función manejadora para Netlify Functions"""
    # Obtener información de la solicitud
    path = event.get('path', '').replace('/.netlify/functions/app', '') or '/'
    method = event.get('httpMethod', 'GET')
    headers = event.get('headers', {})
    body = event.get('body', '')
    
    # Convertir headers a formato Flask
    flask_headers = {}
    for key, value in headers.items():
        flask_headers[key.lower()] = value
    
    # Crear un contexto de solicitud de Flask
    with app.test_request_context(
        path=path,
        method=method,
        headers=flask_headers,
        data=body
    ):
        try:
            # Ejecutar la aplicación Flask
            response = app.full_dispatch_request()
            
            # Convertir la respuesta de Flask a un formato que Netlify entienda
            return {
                'statusCode': response.status_code,
                'headers': dict(response.headers),
                'body': response.get_data(as_text=True)
            }
        except Exception as e:
            # Manejar errores
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': str(e)})
            } 