import string
import random

class PasswordUtils:
    def generate_new_password(self,length):
        characters = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(random.choice(characters) for i in range(length))
        self.save_password_to_env(password)
        
        return password

    def save_password_to_env(password):
        env_file='.env'
        # Leer el contenido del archivo .env
        with open(env_file, 'r') as file:
            lines = file.readlines()
            # Verificar si la variable DB_access_user_PASSWORD ya existe
        updated = False
        for i, line in enumerate(lines):
            if line.startswith('DB_access_user_PASS='):
                lines[i] = f'DB_access_user_PASS={password}\n'
                updated = True

        # Si no se encuentra la variable, agregarla al final
        if not updated:
            lines.append(f'DB_access_user_PASS={password}\n')

        # Escribir el contenido actualizado en el archivo .env
        with open(env_file, 'w') as file:
            file.writelines(lines)
