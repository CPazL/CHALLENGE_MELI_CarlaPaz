import os
import mysql.connector
from mysql.connector import errorcode
from dotenv import load_dotenv
from drive_manager import GoogleDriveManager
from googleapiclient.discovery import build
from datetime import datetime

# Cargar las variables de entorno desde el archivo .env
load_dotenv()
database_name = os.getenv('DB_NAME')
table_name_files_all = os.getenv("TABLE_NAME_FILES")
table_name_files_public = os.getenv("TABLE_NAME_FILES_PUBLIC")
temp_user = os.getenv("DB_TEMP_USER")

class FileInventory:
    ################################ BASE DE DATOS Y TABLAS ################################################

    def verifica_existencia_registro(self, cursor, archivo, tabla, campo):
        try:
            id_buscado = archivo[campo]
            cursor.execute(f"""
                SELECT * FROM {tabla}
                WHERE {campo} = %s
            """, (id_buscado,))
            return cursor.fetchone()
        except mysql.connector.Error as err:
            print(f"Error al verificar existencia del registro en {tabla}: {err}")
            raise

    def visibilidad_actual(self, file, cursor):
        try:
            visibilidad = 'privado' if not GoogleDriveManager.devuelvePermisosPublicosxArchivo(file, cursor) else 'publico'
            return visibilidad
        except Exception as err:
            print(f"Error al determinar la visibilidad del archivo: {err}")
            raise
        
    def actualiza_tabla_archivos(self, cursor, archivo, visibilidad):
        try:
            # Verifica que el archivo no exista dentro de la BASE DE DATOS
            if not self.verifica_existencia_registro(cursor, archivo, table_name_files_all, 'id_archivo'):
                cursor.execute(f"""INSERT INTO {table_name_files_all} 
                                    (id_archivo, nombre, extension, owner, visibilidad, ultima_modificacion) 
                                    VALUES (%s,%s, %s, %s, %s, %s)
                                """, (archivo['id_archivo'], archivo['nombre'], archivo['extension'], archivo['owner'], visibilidad, archivo['fecha_modificacion']))
            else:
                cursor.execute(f"""UPDATE {table_name_files_all} 
                                    SET ultima_modificacion = %s, visibilidad = %s, owner = %s 
                                    WHERE id_archivo = %s
                                """, (archivo['fecha_modificacion'], visibilidad, archivo['owner'], archivo['id_archivo']))
        except mysql.connector.Error as err:
            print(f"Error al actualizar la tabla de archivos: {err}")
            raise

    def actualiza_tabla_archivos_publicos(self, cursor, archivo):
        try:
            if not self.verifica_existencia_registro(cursor, archivo, table_name_files_public, 'archivo_id'):
                cursor.execute(f"""INSERT INTO {table_name_files_public} 
                                    (archivo_id, fecha_cambio)
                                    VALUES (%s, %s)""", (archivo['id_archivo'], archivo['fecha_modificacion']))
        except mysql.connector.Error as err:
            print(f"Error al actualizar la tabla de archivos públicos: {err}")
            raise

    def inventariar_archivos(self, cursor, creds):
        try:
            service = build('drive', 'v3', credentials=creds)

            # Lista los archivos en la cuenta de Google Drive
            results = service.files().list(pageSize=10, fields="nextPageToken, files(id, name)").execute()
            items = results.get('files', [])

            if not items:
                print('No se encontraron archivos.')
            else:
                for item in items:
                    try:
                        visibilidad = self.visibilidad_actual(item, cursor)
                        self.actualiza_tabla_archivos(cursor, item)

                        if visibilidad == 'publico':
                            self.actualiza_tabla_archivos_publicos(cursor, item)
                            GoogleDriveManager.visibilidad_publico_a_privado(item['id'], service)
                            self.actualiza_tabla_archivos(cursor, item, visibilidad)
                    except Exception as err:
                        print(f"Error al procesar el archivo {item['id']}: {err}")
                        raise
        except Exception as err:
            print(f"Error al inventariar archivos: {err}")
            raise
