from flask import Flask, request
from app import app as flask_app
import json

def handler(event, context):
    """Función manejadora para Netlify Functions"""
    # Convertir el evento de Netlify a un objeto de solicitud de Flask
    path = event.get('path', '')
    method = event.get('httpMethod', 'GET')
    headers = event.get('headers', {})
    body = event.get('body', '')
    
    # Crear un contexto de solicitud de Flask
    with flask_app.test_request_context(
        path=path,
        method=method,
        headers=headers,
        data=body
    ):
        # Ejecutar la aplicación Flask
        response = flask_app.full_dispatch_request()
        
        # Convertir la respuesta de Flask a un formato que Netlify entienda
        return {
            'statusCode': response.status_code,
            'headers': dict(response.headers),
            'body': response.get_data(as_text=True)
        } 