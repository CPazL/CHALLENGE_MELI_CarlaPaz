from google.oauth2 import service_account
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError
import os
from notification_manager import MailSenderManager
class GoogleDriveManager:
    def autentificacion_drive(self):
    #Realiza la autenticación con la API de Google Drive y devuelve un objeto de servicio.
        #Defnimos el alcance de acceso
        SCOPES = ['https://www.googleapis.com/auth/drive']
        # Ruta al archivo JSON de credenciales descargado desde la API 
        CREDS_FILE = 'client_secret_drive.json'
        #Se crea la variable que almacenara las credenciales
        creds = None

        # Buscamos si ya existen credenciales almacenadas en un archivo autogenerado llamado token.json
        if os.path.exists('token.json'):
            #Si existe el archivo, utilizamos las credenciales ya almacenados
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            ##Si no hay credenciales guardadas previamente o las credenciales no son validas  
        if not creds or not creds.valid:
            #si las credenciales existen pero las credenciales ya no son validas
            if creds and creds.expired and creds.refresh_token:
                #Generamos un nuevo token de acceso sin necesidad de que el usuario vuelva a autenticarse manualmente 
                creds.refresh(Request())
            else:
                #si la credencial no existe 
                #InstalledAppFlow: Es una clase de la biblioteca google-auth-oauthlib que maneja el flujo de autenticación para nuestra aplicacion de escritorio
                # utilizando a las credenciales descargadas , genera un flujo o flow para solicitar autorización a la API
                flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)
                #guardamos las nuevas credenciales en la variable creds
                creds = flow.run_local_server(port=0)

            # Guarda las credenciales para uso futuro en el archivo token.json
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        #retorna las credenciales permitiendo a nuestra aplicación realizar solicitudes autenticadas a la api de Google Drive creada.      
        return creds
          
    def visibilidad_publico_a_privado(self, file, service):
        file_id= file['id']
    #Esta función recibe como parametros    
        try:

            for permiso in self.obtienePermisosRegistrados(file_id,service):
                #Si el tipo de permiso es para anyone quiere decir que es público
                if permiso.get('type')=='anyone':
                    #Con el objeto  de servicio que permite interactuar con la api de google drive
                    #Eliminamos de la lsita de permisos, todos los que sean publicos
                    service.permissions().delete(fileId=file_id, permissionId=permiso['id'])


       #Excepción cuando hay un error al realizar la solicitud a la API de GOOGLE DRIVE
        except HttpError as error:
                # Manejar el error HTTP
                if error.resp.status == 404:
                    print("Archivo o permiso no encontrado.")
                elif error.resp.status == 403:
                    print("Permisos insuficientes.")
                else:
                    print(f"Error inesperado: {error}")
    #recibe el archivo se ve que tipo de credencial tiene

    def obtienePermisosRegistrados(self,file,service):
        file_id = file['id']
            # Pasandole el ID del archivo, se crea una lsita con los permisos del archivo

        permisos =service.permissions().list(fileId =  file_id).execute()

        return permisos.get('permissions',[])

    def devuelvePermisosPublicosxArchivo(self,file,service):
        file_id = file['id']
       #Filtamos de la lista de permisos , solo los permisos del tipo 'anyone'
        filtered_permisos = [item for item in self.obtienePermisosRegistrados(file_id,service) if item['type'] == 'anyone']
        return filtered_permisos
    
    def verifica_cambio_permisos(self, file, service):

        if not self.devuelvePermisosPublicosxArchivo(file,service):
            owner =file['owners']
            email_list = [owner['emailAddress'] for owner in file.get('owners', [])]
            gmail_service =MailSenderManager.autentificacion_mail()

            for owner_email in email_list:
                MailSenderManager.enviar_notificacion_mail(gmail_service, owner_email, file['name'])
        else:
            print("El cambio de permisos no se realizó correctamente.")


