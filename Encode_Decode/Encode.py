import os
import json
import uuid
import shutil
import pyzipper
from cryptography.fernet import Fernet

def get_uuid():
    new_id = str(uuid.uuid4())
    return new_id

def get_value(nombre_parametro):
    nombre_archivo_json = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Security', 'Parameters.json'))

    if os.path.exists(nombre_archivo_json):
        with open(nombre_archivo_json, "r") as archivo_json_existente:
            contenido = json.load(archivo_json_existente)           
            if nombre_parametro in contenido:
                    return (contenido[nombre_parametro])
            else:
                return (f"El parámetro '{nombre_parametro}' no existe en el archivo JSON.")
    else:
        print(f"El archivo JSON no existe en la ruta: {nombre_archivo_json}")    

def Limpiar_folder(keys_folder):
    for filename in os.listdir(keys_folder):
        file_path = os.path.join(keys_folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)  # Eliminar archivo o enlace simbólico
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)  # Eliminar directorio
        except Exception as e:
            print(f"No se pudo eliminar {file_path}. Razón: {e}")


def generate_name_path(keys_folder):
    new_id = get_uuid()
    key_filename = f"{new_id}.key"  # Asignar el nombre con extensión '.key'
    clave_path = os.path.join(keys_folder, key_filename)

    return clave_path

def generar_clave(): # Función para generar una nueva clave
    clave = Fernet.generate_key()
    
    keys_folder = get_value("keys_folder")
    if not os.path.exists(keys_folder): # Crear la carpeta si no existe
        os.makedirs(keys_folder)
    
    Limpiar_folder(keys_folder)
    
    clave_path = generate_name_path(keys_folder)

    with open(clave_path, "wb") as clave_file: # Guardar la nueva clave
        clave_file.write(clave)

    print(f"Clave generada y guardada en '{clave_path}'.")

    password = get_value("zipp_folder_password")
    Name_file = f"{get_value("zipp_folder_name")}.zip"
  
    # Comprimir la carpeta 'keys' en un archivo zip protegido con contraseña
    comprimir_folder_key(Name_file, keys_folder, password)

def comprimir_folder_key(zip_path, folder_path, password): # Función para comprimir la carpeta Clave en un archivo .zip con contraseña

    ruta_salida = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data')) # Ruta de la carpeta donde se guardará el archivo comprimido

    if not os.path.exists(ruta_salida):# validamos que la carpeta exista
        os.makedirs(ruta_salida)

    ruta_final_zip = os.path.join(ruta_salida, zip_path)# reescribimos la ruta completa

    with pyzipper.AESZipFile(ruta_final_zip, 'w', compression=pyzipper.ZIP_DEFLATED, encryption=pyzipper.WZ_AES) as zf:
        zf.setpassword(password.encode('utf-8'))  # Convertir la contraseña a bytes
        for foldername, subfolders, filenames in os.walk(folder_path):
            for filename in filenames:
                file_path = os.path.join(foldername, filename)
                arcname = os.path.relpath(file_path, folder_path)  # Mantener la estructura de carpetas dentro del ZIP
                zf.write(file_path, arcname)
    
    print(f"Carpeta '{folder_path}' comprimida y guardada como 'data/{zip_path}.zip' protegida con contraseña.") 

def eliminar_carpeta(folder_path): # Función para eliminar la carpeta
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)

def get_key():
    keys_folder = get_value("keys_folder")
    for filename in os.listdir(keys_folder):
        file_path = os.path.join(keys_folder, filename)

    try:
        # Verificar si el archivo de clave existe
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"El archivo de clave '{file_path}' no existe.")

        else:
            # Leer la clave desde el archivo .key
            with open(file_path, "rb") as key_file:
                key = key_file.read()

            return key   

    except FileNotFoundError as e:
        print(e)

def Encrypy_file(nombre_archivo):# Cifra el archivo de configuración

    key = get_key()  # Obtener la clave desde el archivo.key
    fernet = Fernet(key)    

    # Ruta config.yaml 
    ruta_yaml = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Security', nombre_archivo))

    # Ruta donde se guardará el archivo cifrado
    carpeta_salida = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))

    # Asegurarse de que la carpeta de salida (data) exista, si no, crearla
    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)

    # Ruta completa de salida
    ruta_archivo_cifrado = os.path.join(carpeta_salida, nombre_archivo + ".enc")

    try:
        if not os.path.exists(ruta_yaml): # Leer el archivo a cifrar
            raise FileNotFoundError(f"El archivo a cifrar '{ruta_yaml}' no existe.")
        
        with open(ruta_yaml, "rb") as file: # Abrir y leer el archivo original
            archivo_datos = file.read()

        archivo_cifrado = fernet.encrypt(archivo_datos) # Cifrar el archivo
        
        with open(ruta_archivo_cifrado, "wb") as archivo_encrypted: # Guardar el archivo cifrado
            archivo_encrypted.write(archivo_cifrado)    

        print(f"Archivo '{nombre_archivo}' cifrado y guardado como 'data/{nombre_archivo}.end'.")
        
    except FileNotFoundError as e:
        print(e)  # Lógica para guardar log del error



def main():
    # Llamar a la función para generar la clave y comprimirla en un archivo.zip
    generar_clave()

    nombre_archivo = get_value("file_Configurations")
    Encrypy_file(nombre_archivo)

    Encrypy_file("Parameters.json")

    nombre_archivo = get_value("keys_folder")
    eliminar_carpeta(nombre_archivo)

