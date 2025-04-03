import os
import shutil
import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import logging
import json
# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='backup_log.txt'
)

# Configuración de Google Drive API
SCOPES = ['https://www.googleapis.com/auth/drive.file']
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.json'
BACKUP_FOLDER_NAME = 'sistema_cotizaciones_backups'
BACKUP_DIR = 'backups'
DB_FILE = 'sistema_cotizaciones.db'
MAX_BACKUPS = 20  # Máximo número de backups a mantener

def autenticar_drive():
    """Autentica y devuelve un servicio de Google Drive."""
    creds = None
    
    # Verificar si hay un token guardado
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_info(
            json.loads(open(TOKEN_FILE).read()), SCOPES)
    
    # Si no hay credenciales o no son válidas, autenticar
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Asegurar que el archivo de credenciales existe
            if not os.path.exists(CREDENTIALS_FILE):
                logging.error(f"Archivo de credenciales {CREDENTIALS_FILE} no encontrado")
                raise FileNotFoundError(f"Archivo de credenciales {CREDENTIALS_FILE} no encontrado")
            
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Guardar credenciales para la próxima vez
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    
    return build('drive', 'v3', credentials=creds)

def obtener_o_crear_carpeta_backup(service):
    """Obtiene o crea la carpeta de backups en Google Drive."""
    # Buscar la carpeta por nombre
    query = f"name='{BACKUP_FOLDER_NAME}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    response = service.files().list(q=query, spaces='drive',
                                  fields='files(id, name)').execute()
    folders = response.get('files', [])
    
    # Si la carpeta existe, devolver su ID
    if folders:
        folder_id = folders[0]['id']
        logging.info(f"Carpeta de backup encontrada: {folder_id}")
        return folder_id
    
    # Si no existe, crear la carpeta
    folder_metadata = {
        'name': BACKUP_FOLDER_NAME,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    folder = service.files().create(body=folder_metadata, fields='id').execute()
    folder_id = folder.get('id')
    logging.info(f"Carpeta de backup creada: {folder_id}")
    
    return folder_id

def limpiar_backups_antiguos(service, folder_id):
    """Elimina backups antiguos manteniendo solo los últimos MAX_BACKUPS."""
    # Obtener todos los archivos en la carpeta de backup
    query = f"'{folder_id}' in parents and trashed=false"
    response = service.files().list(q=query, spaces='drive',
                                  fields='files(id, name, createdTime)',
                                  orderBy='createdTime').execute()
    files = response.get('files', [])
    
    # Si hay más archivos que el límite, eliminar los más antiguos
    if len(files) > MAX_BACKUPS:
        # Ordenar por fecha de creación (el más antiguo primero)
        files.sort(key=lambda x: x['createdTime'])
        
        # Eliminar los archivos más antiguos
        for file in files[:-MAX_BACKUPS]:
            service.files().delete(fileId=file['id']).execute()
            logging.info(f"Backup antiguo eliminado: {file['name']}")

def realizar_backup():
    """Realiza una copia de la base de datos y devuelve la ruta del archivo."""
    # Crear directorio de backups si no existe
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    
    # Nombre del archivo de backup con timestamp
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f"backup_{timestamp}.db"
    backup_path = os.path.join(BACKUP_DIR, backup_filename)
    
    # Copiar la base de datos actual
    try:
        shutil.copy2(DB_FILE, backup_path)
        logging.info(f"Backup local creado: {backup_path}")
        return backup_path
    except Exception as e:
        logging.error(f"Error al crear backup local: {str(e)}")
        raise

def subir_a_drive(backup_file):
    """Sube el archivo de backup a Google Drive."""
    try:
        # Autenticar con Google Drive
        service = autenticar_drive()
        
        # Obtener o crear carpeta de backups
        folder_id = obtener_o_crear_carpeta_backup(service)
        
        # Nombre del archivo en Google Drive
        file_name = os.path.basename(backup_file)
        
        # Metadata del archivo
        file_metadata = {
            'name': file_name,
            'parents': [folder_id]
        }
        
        # Subir el archivo
        media = MediaFileUpload(backup_file, resumable=True)
        file = service.files().create(body=file_metadata,
                                    media_body=media,
                                    fields='id').execute()
        
        logging.info(f"Backup subido a Google Drive: {file.get('id')}")
        
        # Limpiar backups antiguos
        limpiar_backups_antiguos(service, folder_id)
        
        return file.get('id')
    except Exception as e:
        logging.error(f"Error al subir backup a Google Drive: {str(e)}")
        raise

def main():
    """Función principal para ejecutar el backup."""
    try:
        # Realizar backup local
        backup_file = realizar_backup()
        
        # Subir a Google Drive
        file_id = subir_a_drive(backup_file)
        
        logging.info("Proceso de backup completado con éxito")
        print(f"Backup realizado correctamente. ID en Drive: {file_id}")
        
        return True
    except Exception as e:
        logging.error(f"Error en el proceso de backup: {str(e)}")
        print(f"Error al realizar backup: {str(e)}")
        return False

if __name__ == "__main__":
    # Si se ejecuta directamente, realizar backup
    main()