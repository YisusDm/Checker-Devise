import os
import re
import sys
import yaml
import json
import requests
import Validator
import platform
import subprocess
from datetime import datetime

def cargar_parametros():
    config_file_path = os.path.join('tmp', 'Parameters.json')
    with open(config_file_path, 'r') as f:
        return json.load(f)
    
def cargar_configuracion(): # Carga la configuración desde el archivo YAML

    parametros = cargar_parametros()
    file_Configurations = parametros.get("file_Configurations", "none")

    config_file_path = os.path.join('tmp', file_Configurations)
    try:
        with open(config_file_path, 'r') as config_file:
            configuracion = yaml.safe_load(config_file)
        return configuracion
    except FileNotFoundError:
        print("El archivo de configuración no se encontró.")
        return {}
    except yaml.YAMLError as e:
        print(f"Error al leer el archivo de configuración: {e}")
        return {}

def ejecutar_comando(comando,sistema):

    try:
        if sistema == "Windows":
            # Ejecución de comandos en PowerShell
            resultado = subprocess.run(["powershell", "-Command", comando], capture_output=True, text=True)
            # Ejecución de comandos en PowerShell con permisos de administrador
            #resultado = subprocess.run(["powershell", "-Command", f"Start-Process powershell -ArgumentList '{comando}' -Verb RunAs"], capture_output=True, text=True)
        else:
            # Ejecución de comandos en sistemas basados en Unix (Linux, macOS)
            # resultado = subprocess.run(comando, shell=True, capture_output=True, text=True)
            resultado = subprocess.run(f"sudo {comando}", shell=True, capture_output=True, text=True)

        # Mostramos la salida del comando
        if resultado.stdout:
            print(resultado.stdout)
            return resultado.stdout
        if resultado.stderr:
            print(resultado.stderr)
            return resultado.stderr

    except Exception as e:
        print(f"Error al ejecutar el comando: {e}")

def verificar_procesos(processes_to_check,sistema):
    ls_result = []
    for process in processes_to_check:
        if sistema == "Windows":
            # comando = f"Get-Process -Name {process} -ErrorAction SilentlyContinue"
            comando = f"Get-Process -Name {process} -ErrorAction SilentlyContinue | Select-Object Name, Id, SI, Path, Company"
        else:
            comando = f"pgrep {process}"
        
        result = ejecutar_comando(comando,sistema)
        nresult = (f"{result}")
        ls_result.append(nresult)

    return ls_result

def verificar_puertos(ports_to_check,sistema):
    for port in ports_to_check:
        if platform.system() == "Windows":
            comando = f"netstat -an | findstr : {port}"
            # comando = f"Test-NetConnection -ComputerName localhost -Port {port}"
        else:
            comando = f"netstat -an | grep :{port}"

        result = ejecutar_comando(comando,sistema)
        rdpTraffic = Validator.validar_port(result,port)
    return rdpTraffic 

def verificar_dns(dns_servers,sistema):
    for dns in dns_servers:
        comando = f"nslookup {dns}"
        result = ejecutar_comando(comando,sistema)
        dns_check = Validator.validar_dns(result,dns)
    return dns_check    

def verificar_antivirus(configuracion):
    """Verifica si el proceso del antivirus está en ejecución."""
    comando = configuracion.get('antivirus_check', "Get-Process | Where-Object { $_.ProcessName -eq 'MpDefenderCoreService' }")

    try:
        if platform.system() == "Windows":
            resultado = subprocess.run(["powershell", "-Command", comando], capture_output=True, text=True)
            return "MpDefenderCoreService" in resultado.stdout
        else:
            resultado = subprocess.run(comando, shell=True, capture_output=True, text=True)
            return bool(resultado.stdout.strip())
    except Exception as e:
        print(f"Error al verificar antivirus: {e}")
        return False

def verificar_firewall(sistema):
    
    print("verificando Firewall:")

    if sistema == "Windows":
            # comando = "netsh advfirewall show all | findstr 'disabled'" 
            comando =  "netsh advfirewall show allprofiles"
    else :
        "ufw status"

    result = ejecutar_comando(comando,sistema)
    print("Comprobación Firewall completada.")
    if result is not None:
        if 'DESACTIVAR' in result:
            print("El firewall está desactivado en al menos uno de los perfiles.")
            return True
        else:
            return False
    return False    


def configurar_log():

    parametros = cargar_parametros()
    log_folder = parametros.get("folder_logs", "logs")  # Carpeta por defecto si no se encuentra

    if not os.path.exists(log_folder):
        os.makedirs(log_folder)

    # Asigna nombre al archivo
    fecha_hora = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file_path = os.path.join(log_folder, f"log_{fecha_hora}.txt")

    # Redirigir la salida de print a un archivo
    sys.stdout = open(log_file_path, 'w', encoding='utf-8')

    return log_file_path

def restaurar_print():
    sys.stdout.close()
    sys.stdout = sys.__stdout__


def escribir_archivo_resultados(av_check, dns_check, rdp_check, fw_check, configuracion):
    """Escribe los resultados en archivos de salida."""
    file_managed = configuracion.get('file_managed', "Netskopemanaged.txt")
    file_unmanaged = configuracion.get('file_unmanaged', "UnmanagedDevice.txt")

    try:
        if av_check and dns_check and rdp_check and fw_check:
            with open(file_managed, 'w') as f:
                result = (f"Antivirus Enabled = {av_check}, DNS Server Complaint = {dns_check}, Remote Sessions Disabled = {rdp_check}, Windows Firewall Enabled = {fw_check}")
                f.write(result)
        else:
            with open(file_unmanaged, 'w') as f:
                result = (f"Antivirus Enabled = {av_check}, DNS Server Complaint = {dns_check}, Remote Sessions Disabled = {rdp_check}, Windows Firewall Enabled = {fw_check}")
                f.write(result)
    except Exception as e:
        print(f"Error al escribir los resultados en el archivo: {e}")

def enviar_datos_api(sistema, av_check, dns_check, rdp_check, fw_check):

    # Configurar la conexión con la API
    parametros = cargar_parametros()
    url_api = parametros.get("Url_Api")

    # Prepara los datos a enviar
    data = {
        "kernel": sistema,
        "av_check": av_check,
        "dns_check": dns_check,
        "rdp_check": rdp_check,
        "fw_check": fw_check
    }

    try:
        # Enviar datos a la API
        response = requests.post(url_api, json=data)

        # Verificar si la solicitud fue exitosa
        if response.status_code == 200:
            print("Datos enviados exitosamente a la API.")
        else:
            print(f"Error al enviar datos a la API. Código de estado: {response.status_code}, Mensaje: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión con la API: {e}")

def Get_processes_index(rdp_processes_to_check,Processes):
    filtered_processes = [proc for proc in Processes if proc != 'None']
    Result_Processes = False
    for rdp in rdp_processes_to_check:
        for proc in filtered_processes:
            # Utilizar una expresión regular para extraer el nombre del proceso
            match = re.search(r'Name\s+:\s+(.*)', proc)
            if match:
                process_name = match.group(1).strip()
                if process_name == rdp:
                    Result_Processes = True
                    break 
    return Result_Processes  
          
def play_Test():
    sistema = platform.system()
    print("Starting")
    print(f"Sistema Operativo: {sistema}")
    
    configuracion = cargar_configuracion()
    if not configuracion:
        print("No se pudo cargar la configuración. Saliendo del programa...")
        return
    
    # Reclasificar informacion del archivo YAML
    dns_servers_to_check = configuracion.get("dns_servers", [])
    ports_to_check = configuracion.get("ports", [])

    rdp_processes_to_check = configuracion.get("rdp_processes", [])
    other_processes_to_check = configuracion.get("other_processes", [])
    antivirus_processes_to_check = configuracion.get("antivirus_processes", [])
    

    if dns_servers_to_check:
        print("verificando DNS:")
        dns_check = verificar_dns(dns_servers_to_check,sistema)
        print("Comprobación DNS completada.")
    else:
        print("No hay servidores DNS definidos para verificar.")

    if ports_to_check:
        print("verificando puertos:")
        rdpTraffic = verificar_puertos(ports_to_check,sistema)
        print("Comprobación puertos completada.")
    else:
        print("No hay puertos definidos para verificar.")     

    if rdp_processes_to_check or other_processes_to_check or antivirus_processes_to_check:
        print("Verificando procesos RDP y otros:")
        Processes = verificar_procesos(rdp_processes_to_check,sistema)
        rdpProcesses = Get_processes_index(rdp_processes_to_check,Processes)

        Processes = verificar_procesos(antivirus_processes_to_check,sistema)
        av_check = Get_processes_index(antivirus_processes_to_check,Processes)

        # verificar_procesos(other_processes_to_check,sistema)
        print("Comprobación procesos completada.")
    else:
        print("No hay procesos definidos para verificar.")

    fw_check = verificar_firewall(sistema)

    if rdpTraffic or rdpProcesses:
        rdp_check = True
    else:
        rdp_check = False    

    enviar_datos_api(sistema, av_check, dns_check, rdp_check, fw_check)

    # Escribir resultados
    escribir_archivo_resultados(av_check, dns_check, rdp_check, fw_check, configuracion)

def main():
    log_file = configurar_log()
    play_Test()
    restaurar_print()

# main()    