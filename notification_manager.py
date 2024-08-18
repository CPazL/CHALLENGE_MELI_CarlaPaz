
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
import base64
from email.mime.text import MIMEText
from googleapiclient.errors import HttpError

class MailSenderManager:

    def autentificacion_mail():
        # Autenticación y configuración de Gmail API
        SCOPES = ['https://www.googleapis.com/auth/gmail.send']
        CREDS_FILE = 'client_secret_mail.json'

        try:
            creds = service_account.Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPES)
            gmail_service = build('gmail', 'v1', credentials=creds)
            print('Autenticación exitosa')
            return gmail_service
        except Exception as e:
            print(f'Error durante la autenticación: {e}')
            return None

    def enviar_notificacion_mail(gmail_service, owner_email, file_name):
        if not gmail_service:
            print("Servicio Gmail no autenticado. Llama a 'authenticate_mail()' primero.")
            
        else:
            try:
                # Crear el mensaje de correo electrónico
                message_text = f"Hola,\n\nEl archivo '{file_name}' almacenado en su cuenta de Google Drive ha sido cambiado a privado por motivos de seguridad.\nPerdón por las molestias.\nSaludos,\nEquipo de IT"
                message = MIMEText(message_text)

                message['to'] = owner_email
                message['from'] = os.getenv('EMAIL_SENDER')  # Reemplaza con tu dirección de correo o variable de entorno
                message['subject'] = 'Importante: Cambio de acceso en Google Drive'
                
                # Convertir el mensaje en base64
                raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
                body = {'raw': raw}

                # Enviar el correo
                gmail_service.users().messages().send(userId='me', body=body).execute()
                print(f'Correo enviado a {owner_email} sobre el archivo {file_name}')
            except HttpError as error:
                print(f'Error al enviar el correo electrónico: {error}')
        
    def cerrar_sesion(gmail_service):
        if gmail_service:
            gmail_service.close()  # Aunque no es necesario explícitamente cerrar la sesión en Google API
            print('Sesión de Gmail cerrada correctamente')

