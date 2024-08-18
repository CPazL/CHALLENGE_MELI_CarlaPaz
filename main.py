from googleapiclient.discovery import build
from database_manager import DatabaseManager
from inventory_manager import FileInventory
from drive_manager import GoogleDriveManager
from notification_manager import NotificationManager

def main():
    # Conectar a la base de datos y crearla si no existe
    db_manager = DatabaseManager()
    connection = db_manager.conexion_a_mysql()
    
    if connection:

        cursor = connection.cursor()
        # Crear la base de datos y las tablas si no existen
        db_manager.crear_bd(cursor)

        # Cambiar permisos en Google Drive
        drive_manager = GoogleDriveManager()
        credenciales = drive_manager.autentificacion_drive()
        
        # Inventariar archivos de Google Drive
        inventory_manager = FileInventory(cursor)
        inventory_manager.inventariar_archivos(cursor,credenciales)

        # Cerrar la conexión a la base de datos
        db_manager.cerrar_conexion(cursor)

        connection.close()
    else:
        print("No se pudo conectar a la base de datos.")

if __name__ == "__main__":
    main()


