from flask import Flask, request, Response
import json
import os
import sys

# Agregar el directorio padre al path para poder importar la aplicación principal
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app as flask_app

def handler(event, context):
    """Función manejadora para Netlify Functions"""
    # Obtener información de la solicitud
    path = event.get('path', '')
    method = event.get('httpMethod', 'GET')
    headers = event.get('headers', {})
    body = event.get('body', '')
    
    # Convertir headers a formato Flask
    flask_headers = {}
    for key, value in headers.items():
        flask_headers[key.lower()] = value
    
    # Crear un contexto de solicitud de Flask
    with flask_app.test_request_context(
        path=path,
        method=method,
        headers=flask_headers,
        data=body
    ):
        try:
            # Ejecutar la aplicación Flask
            response = flask_app.full_dispatch_request()
            
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