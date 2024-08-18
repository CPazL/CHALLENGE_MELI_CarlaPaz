import os
from dotenv import load_dotenv

load_dotenv()

database_name = os.getenv('DB_NAME')
table_name_files_all = os.getenv("TABLE_NAME_FILES")
table_name_files_public = os.getenv("TABLE_NAME_FILES_PUBLIC")
temp_user = os.getenv("TEMP_USER")