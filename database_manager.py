import os
import mysql.connector
from mysql.connector import errorcode
from dotenv import load_dotenv
from password_utils import PasswordUtils

# Cargar las variables de entorno desde el archivo .env
load_dotenv()
database_name = os.getenv('DB_NAME')
table_name_files_all=os.getenv("TABLE_NAME_FILES")
table_name_files_public =os.getenv("TABLE_NAME_FILES_PUBLIC")
access_user = os.getenv("DB_access_user")

class DatabaseManager:
    #######################CONEXION########################################
# Función para conectar a la base de datos
    def conexion_a_mysql(self):
        try:

            config = {
                'user': os.getenv('DB_USER'),
                'password': os.getenv('DB_PASSWORD'),#Conseguir contraseña
                'host': os.getenv('DB_HOST'),
                'raise_on_warnings': True
            }
            conn = mysql.connector.connect(**config)
            print("Conexión exitosa a MySQL.")
            return conn
        except mysql.connector.Error as err:
            print(f"Error al conectar a MySQL: {err}")
            return None
    
    #############- cierra conexion----------------
    def cerrar_conexion(self, cursor):
        cursor.close()
    ################ Creación de BD Y TABLAS #################################################
    def crear_bd(self,cursor):
        try:
            cursor.execute(f"CREATE DATABASE {database_name};")
            self.crear_tablas(cursor)
        except mysql.connector.Error as err:
            print(f"Error al conectar a MySQL: {err}")
            raise
    def crear_tablas(self,cursor):
        try :
            #creamos la bs dentro del servidor indicado
            cursor.execute(f"USE {database_name};") 
            #creamos las tablas necesarias
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {table_name_files_all} (
                    id_archivo VARCHAR(255) PRIMARY KEY,
                    nombre VARCHAR(255) NOT NULL,
                    extension VARCHAR(10),
                    owner VARCHAR(255),
                    visibilidad ENUM('privado', 'publico') NOT NULL,
                    ultima_modificacion DATETIME
                );
            """)

            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {table_name_files_public} (
                    id VARCHAR(255) PRIMARY KEY,
                    archivo_id VARCHAR(255),
                    fecha_cambio DATETIME,
                    FOREIGN KEY (archivo_id) REFERENCES {table_name_files_all}(id_archivo)
                );
            """)

            #Luego de creadas las tblas, creamos el usuario que nos va a permitir acceder
            self.crear_usuario(cursor)
            #le asignamos permisos a las tablas necesarias dentro de la bd.
            self.usuario_permisos(cursor)
        except mysql.connector.Error as err:
            print(f"Error al conectar a MySQL: {err}")
            raise

    #################### USUARIO Y PERMISOS #######################################
    def crear_usuario(self, cursor):

        try: 
            length =12
            new_password = PasswordUtils.generate_new_password(length)          
            cursor.execute(f"CREATE USER '{access_user}'@'%' IDENTIFIED BY '{new_password}';")
            print(f"Usuario '{access_user}' creado exitosamente.")

        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_CANNOT_USER:
                print(f"Error al crear el usuario: {err}")
            else:
                raise

    # Función para otorgar permisos
    def usuario_permisos(self,cursor):
        try:
            cursor.execute(f"GRANT CREATE ON {database_name}.* TO '{self.access_user}'@'%';")
            print(f"Permiso 'CREATE' otorgado al usuario '{self.access_user}' sobre la base de datos '{database_name}'.")
            
            cursor.execute(f"GRANT CREATE, ALTER, DROP, INSERT, UPDATE, DELETE, SELECT ON `{table_name_files_all}`.* TO '{access_user}'@'%';")
            print(f"Permisos otorgados al usuario '{self.access_user}' sobre la tabla '{table_name_files_all}'.")
            
            cursor.execute(f"GRANT CREATE, ALTER, DROP, INSERT, UPDATE, DELETE, SELECT ON `{table_name_files_public}`.* TO '{access_user}'@'%';")
            print(f"Permisos otorgados al usuario '{self.access_user}' sobre la tabla '{table_name_files_public}'.")
            
            cursor.execute("FLUSH PRIVILEGES;")
            print("Privilegios aplicados exitosamente.")

        except mysql.connector.Error as err:
            print(f"Error al otorgar permisos: {err}")
            raise

    def elimina_usuario(self,cursor):
        # Eliminar el usuario temporal
        try:
            cursor.execute(f"DROP USER '{access_user}'@'%';")
            print(f"Usuario '{access_user}' eliminado exitosamente.")

        except mysql.connector.Error as err:
            print(f"Error al eliminar el usuario: {err}")
            raise

    