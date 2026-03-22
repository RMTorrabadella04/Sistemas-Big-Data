# 1. Conexión con la base de datos.
En comparación con la práctica 1.7, esta vez hemos querido llevar el acceso de la base de datos fuera del entorno local, así simulando un situación real. Mediante el uso de un servidor proxmox y una mv
Debian, hemos alojado la base de datos utilizando MariaDB, y ssh en la conexión de la base de datos y un equipo (ambos en redes distintas - uso de ip pública y autenticación usuario/contraseña tanto en
el servidor como en MariaDB)
# 2. Extración y limpieza de los datos.
A partir de un Script desarrollado con el lenguaje Python, generamos una conexión ssh con el serviodor, y mediante querys guardamos todos los datos en DataFrames de la librería Polars. Una vez obtenido 
los datos, nos aseguramos de realizarle un "limpieza" para asegurarnos de que no existiera algún dato nulo, incorrecto o simplemente convertirlo en un dato más legible.
# 3. Creación de gráficos
Con la ayuda de Plotly, creamos algunos gráficos sobre temas relevantes a nuestros datos (IPV y IPC).

## Gráfico 1
![IMagen no disponibel](ipc_vs_ipv_1.7.png)

Comparativa del IPC y IPV a lo largo de 2018 hasta 2024. Ambas presentan variaciones notables: la línea roja comienza en un valor medio, experimenta ligeras fluctuaciones, luego alcanza un pico pronunciado hacia la parte derecha antes de descender; mientras que la línea azul parece seguir una tendencia más irregular, con subidas y bajadas más marcadas, llegando también a valores altos en la zona final.

## Gráfico 2
![IMagen no disponibel](ipv_espanya_1.7.png)

Representación del ipv mediante la utilización de un mapa de españa, además del uso de colores explicando a lo largo de los años una situación más o menos favorable en las distintas comunidades.

## Gráfico 3
![IMagen no disponibel](ipv_heatmap_1.7.png)

El heatmap muestra la evolución de la variación anual del Índice de Precios de la Vivienda (IPV) por trimestres entre 2007 y 2025, donde los colores representan la intensidad del cambio: tonos rojos indican fuertes subidas, mientras que los colores más claros reflejan crecimientos débiles o caídas. Se observa un periodo de gran crecimiento en 2007–2008, seguido de una fase prolongada de descenso o estancamiento entre 2009 y 2013. A partir de 2014, el mercado se recupera con aumentos sostenidos hasta 2019, mientras que en 2020 hay una ligera moderación. Posteriormente, destaca un nuevo repunte en 2021–2022 con incrementos intensos, seguido de cierta estabilización en 2023–2024, manteniéndose en niveles positivos.

## Gráfico 4
![IMagen no disponibel](ranking_ccaa_crecimiento_1.7.png)

Este gráfico de barras muestra el crecimiento total acumulado del precio de la vivienda entre 2018 y 2024 por comunidades autónomas en España. Se observa una clara diferencia territorial, destacando Ceuta y Melilla como las zonas con mayor incremento, seguidas de regiones como Andalucía y Baleares, que también presentan subidas muy significativas. En un nivel intermedio se sitúan comunidades como Madrid, Cataluña y la Comunitat Valenciana, con crecimientos elevados pero más moderados. Por el contrario, regiones como Extremadura y Castilla-La Mancha registran los menores aumentos. En conjunto, el gráfico refleja un crecimiento generalizado del precio de la vivienda en todo el país, aunque con importantes desigualdades según la región.
