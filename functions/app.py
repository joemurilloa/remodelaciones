from flask import Flask, Response, jsonify
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
    try:
        # Retornar una respuesta simple para probar
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'message': 'API funcionando correctamente',
                'path': event.get('path', ''),
                'method': event.get('httpMethod', 'GET')
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'error': str(e)
            })
        } 