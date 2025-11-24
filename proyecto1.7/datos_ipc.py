import requests
import json
import mysql.connector

URL1 = "https://servicios.ine.es/wstempus/js/ES/DATOS_SERIE/IPC251856?nult=100"
data = requests.get(URL1).json()

conexion = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="fila_2"
)

cursor = conexion.cursor()
contador = 1

for i in range(1):
    cursor.execute(
        "INSERT INTO ipc (COD, Nombre) VALUES (%s, %s)",
        (data["COD"], data["Nombre"])
    )
    for x in data['Data']:
        cursor.execute(
            "INSERT INTO data_ipc (Fecha, FK_Periodo, Anyo, Valor, id_ipc) VALUES (%s, %s, %s, %s, %s)",
            (x["Fecha"], x["FK_Periodo"], x["Anyo"], x["Valor"], contador)
        )
    contador += 1
conexion.commit()
cursor.close()
conexion.close()

print("✅ Datos insertados correctamente ")