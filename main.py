import paramiko
# Parche para versiones modernas de paramiko
if not hasattr(paramiko, 'DSSKey'):
    paramiko.DSSKey = paramiko.dsskey.DSSKey

from sshtunnel import SSHTunnelForwarder
import pymysql
import polars as pl

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

if __name__ == "__main__":
    conexionBBDD_SSH()