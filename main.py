import paramiko
# Parche para versiones modernas de paramiko
if not hasattr(paramiko, 'DSSKey'):
    paramiko.DSSKey = paramiko.dsskey.DSSKey

from sshtunnel import SSHTunnelForwarder
import pymysql
import polars as pl
from datetime import datetime


def conexionBBDD_SSH():
    VM_IP = '79.112.2.0' 
    SSH_USER = 'usu'
    SSH_PASS = 'usu'

    # --- DATOS DE MARIADB (La base de datos) ---
    DB_USER = 'remoto' 
    DB_PASS = 'clave_segura'
    DB_NAME = 'fila_2'

    # Creamos el túnel
    with SSHTunnelForwarder(
        (VM_IP, 20000),
        ssh_username=SSH_USER,
        ssh_password=SSH_PASS,
        remote_bind_address=('127.0.0.1', 3306)
    ) as tunnel:

        # Ahora conectamos como si la DB estuviera en tu propio PC (localhost)
        # pero a través del puerto que el túnel ha abierto
        db = pymysql.connect(
            host='127.0.0.1',
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME,
            port=tunnel.local_bind_port
        )


        cursor = db.cursor()
        
        tablas = ["ipv", "data_ipv", "ipc", "data_ipc"]
        
        dfs = {}
        
        for tabla in tablas:
            cursor.execute(f"SELECT * FROM {tabla}")
            resultados = cursor.fetchall()
            columnas = [desc[0] for desc in cursor.description]
            
            dfs[tabla] = pl.DataFrame(resultados, schema=columnas, strict=False)
            print(f"✓ {tabla}: {len(dfs[tabla])} filas")

        db.close()
        
        return dfs

def verificarDatos(dfs):
    for nombre, df in dfs.items():
        print(f"\n--- {nombre} ---")
        print(df.head())
        print(f"Columnas: {df.columns}")
        print(f"Tipos de datos: {df.dtypes}")
        print(f"Valores nulos: \n{df.null_count().sum()}\n")
        print(f"Total filas: {len(df)}")
        
        # Cambiaremos el formato de fecha si existe la columna 'fecha'
        if 'Fecha' in df.columns:
            df = df.with_columns(
                pl.col('Fecha').map_elements(
                    lambda x: milisegundos_a_fecha(x), 
                    return_dtype=pl.Datetime
                ).alias('Fecha')
            )
        print(df.head())



def milisegundos_a_fecha(ms, tz=None):
    ms = int(ms)
    # Validación de entrada
    if not isinstance(ms, (int, float)):
        raise ValueError("El valor debe ser un número (int o float).")
    
    try:
        # Convertir milisegundos a segundos
        segundos = ms / 1000.0
        return datetime.fromtimestamp(segundos, tz=tz)
    except (OverflowError, OSError) as e:
        raise ValueError(f"El valor de milisegundos no es válido: {e}")


if __name__ == "__main__":
    datos = conexionBBDD_SSH()
    
                            # Verificando podemos ver que no tenemos datos nulos, 
    verificarDatos(datos)   # además de qestar bien formateados y estructurados ha excepción de las fechas
                            # para hacer unos gráficos con plotly 
    
