from flask import Flask, request, jsonify 
import pyodbc

app = Flask(__name__)

connection_string = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=(localdb)\\MSSQLLocalDB;DATABASE=ManageDevise;Trusted_Connection=yes;'

try:
    conn = pyodbc.connect(connection_string)
    print("Conexión exitosa")
    conn.close()
except Exception as e:
    print(f"Error de conexión: {e}")

# Función para insertar datos usando el procedimiento almacenado
def insert_device_check(kernel, av_check, dns_check, rdp_check, fw_check):
    try:
        # Conectar a la base de datos
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        # Ejecutar el procedimiento almacenado
        cursor.execute("""
            EXEC InsertDeviceCheck @Kernel=?, @av_check=?, @dns_check=?, @rdp_check=?, @fw_check=?
        """, kernel, av_check, dns_check, rdp_check, fw_check)

        # Confirmar los cambios
        conn.commit()

        # Cerrar la conexión
        cursor.close()
        conn.close()

        return {"message": "Datos insertados correctamente"}, 200

    except Exception as e:
        return {"error": str(e)}, 500

# Ruta para manejar la solicitud POST
@app.route('/insert', methods=['POST'])
def insert_data():
    try:
        # Obtener los datos del cuerpo de la solicitud
        data = request.json
        kernel = data.get('kernel')
        av_check = data.get('av_check')
        dns_check = data.get('dns_check')
        rdp_check = data.get('rdp_check')
        fw_check = data.get('fw_check')

        # Llamar a la función para insertar los datos
        return insert_device_check(kernel, av_check, dns_check, rdp_check, fw_check)

    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Ejecutar la API
if __name__ == '__main__':
    app.run(debug=True)
