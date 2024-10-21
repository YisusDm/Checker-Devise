
def validar_dns(entrada,dns):
    try:
        lineas = entrada.split("\n")
    except AttributeError as e:
        print(f"Error: La entrada es None o no es una cadena válida. Detalles: {e}")
        return False  # o cualquier valor que desees retornar en caso de error
    
    servidor = ""
    address_servidor = ""
    nombre_dns = ""
    address_dns = ""

    for linea in lineas:
        if "Servidor:" in linea:
            servidor = linea.split(":")[1].strip()
        elif "Address:" in linea and not address_servidor:
            address_servidor = linea.split(":")[1].strip()
        elif "Nombre:" in linea:
            nombre_dns = linea.split(":")[1].strip()
        elif "Address:" in linea and not address_dns:
            address_dns = linea.split(":")[1].strip()
    
    # Validaciones
    if servidor != "UnKnown":
        if address_dns != "8.8.8.8" and address_dns != "1.1.1.1":
            if address_servidor == dns:
                return True
            else:
                return False
        else:
            print(f"Address DNS no es válido: {address_dns}")
            return False
    else:
        print(f"Servidor no es válido: {servidor}")
        return False


def validar_port(result, port):
    try:
        # Crear el patrón de coincidencia que vamos a buscar
        mensaje_error = f"FINDSTR: No se puede abrir {port}"
        
        # Verificar si el mensaje de error está en el resultado
        if result is None:
            raise ValueError("El resultado es None. Verifique la entrada.")
        
        if mensaje_error in result:
            return False
        else:
            return True
    except TypeError as e:
        print(f"Error: Se ha producido un error de tipo. Detalles: {e}")
        return False
    except ValueError as ve:
        print(ve)
        return False