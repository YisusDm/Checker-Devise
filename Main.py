import os
import json
import shutil
import Checker
from datetime import datetime
from Encode_Decode import Encode
from Encode_Decode import Decode  
from Encode_Decode import NewId 

data_folder = os.path.abspath(os.path.join('data'))
tmp_folder = os.path.abspath(os.path.join('tmp'))

def cargar_parametros():
    config_file_path = os.path.join('tmp', 'Parameters.json')
    if os.path.exists(config_file_path):
        with open(config_file_path, 'r') as f:
            return json.load(f)
    else:
        print(f"Archivo de configuración no encontrado: {config_file_path}")
        return None    

def validar_carpeta_tmp():

    if os.path.exists(tmp_folder):
        parametros = cargar_parametros()
        if parametros is not None:
            file_Configurations = parametros.get("file_Configurations", "none")
            if os.path.isfile(os.path.join(tmp_folder, file_Configurations)):
                print(f"Archivo de configuración encontrado: {file_Configurations}")
                return True
            else:
                print(f"Archivo de configuración no encontrado: {file_Configurations}")
                return False
        else:
            return False
    else:
        print(f"Carpeta 'tmp' no existe: {tmp_folder}")
        return False
    
def validar_carpeta_data():

    if os.path.exists(data_folder):
        enc = encontrar_archivos_enc()
        zip = encontar_zip_data()
        if zip >= 1 and enc >= 1 :
            return True
        else:
            print("Uno o ambos archivos no se encuentran en la carpeta 'data'")
            return False # continua proceso de codificacion
    else:
        print(f"Carpeta 'data' no existe: {data_folder}")
        return False # continua proceso de codificacion
    
def encontar_zip_data():
    count_zip = 0
    # Buscar el único archivo .zip en la carpeta 'data'
    for archivo in os.listdir(data_folder):
        if archivo.endswith(".zip"):
            count_zip += 1           
    return count_zip 

def encontrar_archivos_enc():
    count_enc = 0
    for archivo in os.listdir(data_folder):
        if archivo.endswith(".enc"):
            count_enc += 1
    return count_enc

def codificar_data():
    print("Codificion iniciada...")
    Encode.main()
    print("Codificación finalizada.")

def decodificar_data():
    print("Decodificion iniciada...")
    Decode.main()
    print("Decodificación finalizada.")

def eliminar_carpeta(folder_path): # Función para eliminar la carpeta
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)  


def main():
    if validar_carpeta_tmp() == True:
        Checker.main()
        eliminar_carpeta(tmp_folder)
    else:
        if validar_carpeta_data() == True:
            decodificar_data()
            main()
        elif validar_carpeta_data() == False:
            codificar_data()
            main()
        else:
            print("No se encontraron archivos para codificar o decodificar.")

        
main()