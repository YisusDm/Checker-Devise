import os
import sys
import time
import win32serviceutil
import win32service
import win32event
import servicemanager
import subprocess
import socket
import logging

# Configuración de logging
LOG_PATH = r"C:\Software_Develop\Repositorios_Lenguaje\Python\Scripts\Proyecto-ManageDeviceCheckerService\service.log"
GET_CLOCK_SCRIPT = os.path.join(os.path.dirname(__file__), 'Main.py')

logging.basicConfig(
    filename=LOG_PATH,
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Clase del servicio
class CheckerDeviceService(win32serviceutil.ServiceFramework):
    _svc_name_ = "CheckerDeviceService"
    _svc_display_name_ = "Checker Device Service"
    _svc_description_ = "Este es un servicio que comprueba la seguridad de una máquina constantemente"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.stop_requested = False
        logging.debug("Servicio CheckerDevice iniciado - inicializando.")
        socket.setdefaulttimeout(60)  # Timeout de socket (puede ser eliminado si no es necesario)

    def SvcStop(self):
        """Se ejecuta cuando el servicio se detiene."""
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.stop_requested = True
        servicemanager.LogInfoMsg("Deteniendo el servicio CheckerDevice...")
        logging.info("Servicio CheckerDevice detenido.")

    def SvcDoRun(self):
        """Se ejecuta cuando el servicio se inicia."""
        servicemanager.LogInfoMsg("Iniciando el servicio CheckerDevice...")
        logging.info("Iniciando CheckerDevice...")

        # Informar a Windows que estamos listos para correr
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)

        # Verificar si el archivo Main.py existe antes de ejecutarlo
        if not os.path.exists(GET_CLOCK_SCRIPT):
            servicemanager.LogErrorMsg(f"No se encontró el archivo {GET_CLOCK_SCRIPT}")
            logging.error(f"No se encontró el archivo {GET_CLOCK_SCRIPT}")
            return

        # Verificar si tenemos permisos para escribir en el log
        if not self.check_write_permissions(os.path.dirname(LOG_PATH)):
            logging.error(f"No hay permisos de escritura en {os.path.dirname(LOG_PATH)}. Terminando servicio.")
            servicemanager.LogErrorMsg(f"No hay permisos de escritura en {os.path.dirname(LOG_PATH)}. Terminando servicio.")
            return

        # Ejecutar el script Main.py mientras el servicio esté corriendo
        self.run_main_script(GET_CLOCK_SCRIPT)

    def run_main_script(self, script_path):
        servicemanager.LogInfoMsg("Ejecutando el script Main.py...")
        logging.info("Ejecutando Main.py...")

        while not self.stop_requested:
            try:
                # Ejecutar el script Main.py
                process = subprocess.Popen([sys.executable, script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                timeout = 0
                timeout_limit = 300  # Timeout en segundos (5 minutos)

                while process.poll() is None and not self.stop_requested:
                    time.sleep(1)
                    timeout += 1

                    # Si el proceso tarda más de timeout_limit segundos, lo terminamos
                    if timeout > timeout_limit:
                        process.terminate()
                        servicemanager.LogErrorMsg(f"Main.py ha excedido el límite de {timeout_limit} segundos. Terminando proceso.")
                        logging.error(f"Main.py ha excedido el límite de {timeout_limit} segundos. Terminando proceso.")
                        break

                # Si el servicio se detiene, terminar el proceso si sigue activo
                if self.stop_requested and process.poll() is None:
                    process.terminate()
                    servicemanager.LogInfoMsg("Main.py ha sido terminado correctamente.")
                    logging.info("Main.py ha sido terminado correctamente.")

                # Capturar y registrar cualquier error
                if process.poll() != 0:
                    stdout, stderr = process.communicate()
                    servicemanager.LogErrorMsg(f"Error ejecutando Main.py: {stderr.decode('utf-8')}")
                    logging.error(f"Error ejecutando Main.py: {stderr.decode('utf-8')}")

            except Exception as e:
                servicemanager.LogErrorMsg(f"Excepción en la ejecución de Main.py: {str(e)}")
                logging.error(f"Excepción en la ejecución de Main.py: {str(e)}")

            # Esperar 60 segundos antes de volver a ejecutar el script
            time.sleep(60)

    def check_write_permissions(self, directory):
        """Verifica si hay permisos de escritura en el directorio especificado."""
        try:
            testfile = os.path.join(directory, "test_write_permissions.txt")
            with open(testfile, 'w') as f:
                f.write("Prueba de permisos de escritura.")
            os.remove(testfile)  # Eliminar archivo de prueba
            return True
        except Exception as e:
            logging.error(f"Error verificando permisos de escritura: {str(e)}")
            return False


if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(CheckerDeviceService)
    import sys
    if len(sys.argv) == 1:
        # Solo para pruebas locales: Comentar estas líneas
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(CheckerDeviceService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(CheckerDeviceService)
