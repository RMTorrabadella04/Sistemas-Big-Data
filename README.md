# 1. Conexión con la base de datos.
En comparación con la práctica 1.7, esta vez hemos querido llevar el acceso de la base de datos fuera del entorno local, así simulando un situación real. Mediante el uso de un servidor proxmox y una mv
Debian, hemos alojado la base de datos utilizando MariaDB, y ssh en la conexión de la base de datos y un equipo (ambos en redes distintas - uso de ip pública y autenticación usuario/contraseña tanto en
el servidor como en MariaDB)
# 2. Extración y limpieza de los datos.
A partir de un Script desarrollado con el lenguaje Python, generamos una conexión ssh con el serviodor, y mediante querys guardamos todos los datos en DataFrames de la librería Polars. Una vez obtenido 
los datos, nos aseguramos de realizarle un "limpieza" para asegurarnos de que no existiera algún dato nulo, incorrecto o simplemente convertirlo en un dato más legible.
# 3. Creación de gráficos
Con la ayuda de Plotly, creamos algunos gráficos sobre temas relevantes a nuestros datos (IPV y IPC).
