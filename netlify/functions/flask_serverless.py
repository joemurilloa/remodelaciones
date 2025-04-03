import os
import sys
import json
from urllib.parse import parse_qs

# Agregar el directorio raíz al path de Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Importar la aplicación Flask
from app import app

def handler(event, context):
    """
    Función para manejar solicitudes en un entorno serverless de Netlify.
    Este script convierte solicitudes de API Gateway a solicitudes WSGI
    y viceversa.
    """
    # Obtener detalles de la solicitud
    path = event.get('path', '/')
    http_method = event.get('httpMethod', 'GET')
    headers = event.get('headers', {})
    
    # Obtener parámetros de consulta
    query_string = event.get('queryStringParameters', {}) or {}
    query_string = '&'.join([f"{k}={v}" for k, v in query_string.items()])
    
    # Obtener cuerpo de la solicitud
    body = event.get('body', '')
    if event.get('isBase64Encoded', False):
        import base64
        body = base64.b64decode(body)
    
    # Crear entorno WSGI
    environ = {
        'REQUEST_METHOD': http_method,
        'PATH_INFO': path,
        'QUERY_STRING': query_string,
        'CONTENT_LENGTH': str(len(body) if body else 0),
        'SERVER_NAME': 'netlify',
        'SERVER_PORT': '443',
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'https',
        'wsgi.input': body if body else b'',
        'wsgi.errors': sys.stderr,
        'wsgi.multithread': False,
        'wsgi.multiprocess': False,
        'wsgi.run_once': False,
    }
    
    # Agregar cabeceras HTTP
    for key, value in headers.items():
        key = key.upper().replace('-', '_')
        if key not in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
            key = f'HTTP_{key}'
        environ[key] = value
    
    # Variables para la respuesta
    response_body = []
    response_headers = {}
    response_status = '200 OK'
    
    # Función para capturar la respuesta de Flask
    def start_response(status, headers):
        nonlocal response_status, response_headers
        response_status = status
        response_headers = dict(headers)
    
    # Ejecutar la aplicación Flask
    for chunk in app(environ, start_response):
        response_body.append(chunk)
    
    # Compilar la respuesta
    response = {
        'statusCode': int(response_status.split(' ')[0]),
        'headers': response_headers,
        'body': b''.join(response_body).decode('utf-8'),
        'isBase64Encoded': False
    }
    
    return response