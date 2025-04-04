import json

def handler(event, context):
    """Función manejadora para Netlify Functions"""
    try:
        # Obtener el path y método de la solicitud
        path = event.get('path', '').replace('/.netlify/functions/app', '') or '/'
        method = event.get('httpMethod', 'GET')
        
        # Manejar diferentes rutas
        if path == '/' and method == 'GET':
            response_body = {
                'message': 'API funcionando correctamente',
                'status': 'success'
            }
        elif path == '/api/cotizacion' and method == 'POST':
            response_body = {
                'message': 'Endpoint de cotización',
                'status': 'success'
            }
        else:
            response_body = {
                'message': f'Ruta no encontrada: {path}',
                'status': 'error'
            }
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json'
                },
                'body': json.dumps(response_body)
            }

        # Retornar respuesta exitosa
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
            },
            'body': json.dumps(response_body)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'message': str(e),
                'status': 'error'
            })
        } 