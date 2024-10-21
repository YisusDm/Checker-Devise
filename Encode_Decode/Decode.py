import os
import pyzipper
from cryptography.fernet import Fernet
import time
import threading
import shutil

# Ruta de la carpeta 'data' y 'tmp'
data_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
tmp_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'tmp'))


# Función para limpiar la carpeta 'tmp' si ya contiene archivos
def limpiar_carpeta_tmp():
    if os.path.exists(tmp_folder):
        # Si la carpeta 'tmp' contiene archivos, los eliminamos
        for archivo in os.listdir(tmp_folder):
            archivo_path = os.path.join(tmp_folder, archivo)
            try:
                if os.path.isfile(archivo_path) or os.path.islink(archivo_path):
                    os.unlink(archivo_path)  # Eliminar archivos y enlaces
                elif os.path.isdir(archivo_path):
                    shutil.rmtree(archivo_path)  # Eliminar carpetas y su contenido
            except Exception as e:
                print(f"Error al eliminar el archivo {archivo_path}: {e}")
    else:
        # Si no existe, la creamos
        os.makedirs(tmp_folder)
        print(f"Carpeta 'tmp' creada en: {tmp_folder}")

# Función para encontrar el archivo .key en la carpeta 'data'
def encontrar_archivo_key():
    for archivo in os.listdir(data_folder):
        if archivo.endswith(".key"):
            return os.path.join(data_folder, archivo)
    raise FileNotFoundError("No se encontró ningún archivo '.key' en la carpeta 'data'.")

# Función para eliminar el archivo .key después de N segundos
def eliminar_archivo_con_retraso(archivo,delay):
    def eliminar_archivo():
        time.sleep(delay)  # Espera de (delay) segundos
        if os.path.exists(archivo):
            os.remove(archivo)
            print(f"Archivo eliminado después de {delay} segundos.")
        else:
            print(f"Archivo no encontrado o ya eliminado.")
    
    # Crear un hilo para ejecutar la eliminación sin bloquear el programa principal
    thread = threading.Thread(target=eliminar_archivo)
    thread.start()

# Función para buscar el archivo zip y extraer la clave
def extraer_zip_con_password():
    zip_file = None
    # Buscar el único archivo .zip en la carpeta 'data'
    for archivo in os.listdir(data_folder):
        if archivo.endswith(".zip"):
            zip_file = os.path.join(data_folder, archivo)
            break
    
    if zip_file is None:
        raise FileNotFoundError("No se encontró ningún archivo '.zip' en la carpeta 'data'.")

    # Intentar abrir el archivo .zip con una contraseña
    # password = input("Introduce la contraseña para el archivo .zip: ")
    password = "A1b2345"
    try:
        with pyzipper.AESZipFile(zip_file, 'r') as zf:
            zf.setpassword(password.encode('utf-8'))  # Convertir la contraseña en bytes
            zf.extractall(data_folder)  # Extraer todos los archivos en la carpeta 'data'
            print(f"Archivo .zip extraído correctamente.")
    except Exception as e:
        print(f"Error al extraer el archivo .zip: {e}")

# Función para desencriptar un archivo .enc
def desencriptar_archivo(nombre_archivo_enc):
    archivo_key = encontrar_archivo_key()
    with open(archivo_key, "rb") as clave_file:
        clave = clave_file.read()

    fernet = Fernet(clave)

    with open(nombre_archivo_enc, "rb") as archivo_encrypted:
        archivo_datos = archivo_encrypted.read()

    archivo_descifrado = fernet.decrypt(archivo_datos)
    return archivo_descifrado

def guardar_archivo_desencriptado(nombre_archivo_enc,archivo_descifrado): # Escribir el archivo desencriptado en la carpeta 'tmp'
    nombre_archivo_original = os.path.basename(nombre_archivo_enc).replace(".enc", "")
    ruta_archivo_desencriptado = os.path.join(tmp_folder, nombre_archivo_original)
    with open(ruta_archivo_desencriptado, "wb") as archivo_desencriptado:
        archivo_desencriptado.write(archivo_descifrado)


# Ejecución del proceso completo
def main():

    limpiar_carpeta_tmp()
    # Extraer el archivo zip y obtener la clave
    extraer_zip_con_password()

    # Desencriptar todos los archivos .enc en la carpeta 'data' y guardarlos en 'tmp'
    for archivo in os.listdir(data_folder):
        if archivo.endswith(".enc"):
            archivo_enc = os.path.join(data_folder, archivo)
            datos_desencriptados = desencriptar_archivo(archivo_enc)
            guardar_archivo_desencriptado(archivo_enc, datos_desencriptados)
            print(f"Archivo '{archivo}' desencriptado correctamente.")

    # Encontrar el archivo .key y eliminarlo
    archivo_key = encontrar_archivo_key()
    eliminar_archivo_con_retraso(archivo_key,1)

# main()