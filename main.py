import paramiko
if not hasattr(paramiko, 'DSSKey'):
    paramiko.DSSKey = paramiko.dsskey.DSSKey

from sshtunnel import SSHTunnelForwarder
import pymysql
import polars as pl
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import requests
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

# Verifica que todos los DataFrames estén correctamente formateados, 
# sin valores nulos y con las fechas convertidas a formato datetime 
# para facilitar su uso en gráficos y análisis posteriores. 
def verificarDatos(dfs):
    for nombre, df in dfs.items():
        print(f"\n--- {nombre} ---")
        print(df.head())
        print(f"Columnas: {df.columns}")
        print(f"Tipos de datos: {df.dtypes}")
        print(f"Valores nulos: \n{df.null_count().sum()}\n")
        print(f"Total filas: {len(df)}")
        
        if 'Fecha' in df.columns:
            df = df.with_columns(
                pl.col('Fecha').map_elements(
                    lambda x: milisegundos_a_fecha(x), 
                    return_dtype=pl.Datetime
                ).alias('Fecha')
            )
            dfs[nombre] = df
        print(df.head())
    
    return dfs

# Función que pasa de milisegundos a formato datetime.

def milisegundos_a_fecha(ms, tz=None):
    ms = int(ms)
    if not isinstance(ms, (int, float)):
        raise ValueError("El valor debe ser un número (int o float).")
    
    try:
        segundos = ms / 1000.0
        return datetime.fromtimestamp(segundos, tz=tz)
    except (OverflowError, OSError) as e:
        raise ValueError(f"El valor de milisegundos no es válido: {e}")

# Las siguientes funciones son para crear gráficos con plotly

def graficoIPCeIPV(dfs):
    df_ipc = dfs['data_ipc'].filter(
        (pl.col('Fecha') >= datetime(2018, 1, 1)) & 
        (pl.col('Fecha') <= datetime(2024, 1, 1))
    )
    df_ipv = dfs['data_ipv'].filter(
        (pl.col('Id_ipv') == 3) &
        (pl.col('Fecha') >= datetime(2018, 1, 1)) & 
        (pl.col('Fecha') <= datetime(2024, 1, 1))
    )

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_ipc['Fecha'],
        y=df_ipc['Valor'],
        name='IPC %',
        yaxis='y1'
    ))

    fig.add_trace(go.Scatter(
        x=df_ipv['Fecha'],
        y=df_ipv['Valor'],
        name='IPV %',
        yaxis='y1'  
    ))

    fig.update_layout(
        title='Evolución IPC vs IPV (2018-2024)',
        yaxis=dict(title='Variación %'),
    )
    fig.write_html("ipc_vs_ipv.html")

def graficoIPVEspanya(dfs):
    geojson_url = "https://raw.githubusercontent.com/codeforgermany/click_that_hood/main/public/data/spain-communities.geojson"
    geojson = requests.get(geojson_url).json()
    
    ids_ccaa = dfs['ipv'].filter(
        pl.col('Nombre').str.contains('General. Variación anual')
    ).select('id', 'Nombre')

    mapa_comunidades = {
        'Andalucía': 'Andalucia',
        'Aragón': 'Aragon',
        'Asturias, Principado de': 'Asturias',
        'Balears, Illes': 'Baleares',
        'Canarias': 'Canarias',
        'Cantabria': 'Cantabria',
        'Castilla y León': 'Castilla-Leon',
        'Castilla - La Mancha': 'Castilla-La Mancha',
        'Cataluña': 'Cataluña',
        'Comunitat Valenciana': 'Valencia',
        'Extremadura': 'Extremadura',
        'Galicia': 'Galicia',
        'Madrid, Comunidad de': 'Madrid',
        'Murcia, Región de': 'Murcia',
        'Navarra, Comunidad Foral de': 'Navarra',
        'País Vasco': 'Pais Vasco',
        'Rioja, La': 'La Rioja',
        'Ceuta': 'Ceuta',
        'Melilla': 'Melilla'
    }

    filas = []
    for row in ids_ccaa.iter_rows(named=True):
        nombre = row['Nombre'].split('.')[0].strip()
        nombre_geo = mapa_comunidades.get(nombre)
        if not nombre_geo:
            continue

        df_ccaa = dfs['data_ipv'].filter(
            (pl.col('Id_ipv') == row['id']) &
            (pl.col('Fecha') >= datetime(2018, 1, 1)) &
            (pl.col('Fecha') <= datetime(2024, 6, 30))
        ).sort('Fecha')

        for r in df_ccaa.iter_rows(named=True):
            filas.append({
                'comunidad': nombre_geo,
                'fecha': str(r['Fecha'])[:7],
                'valor': r['Valor']
            })

    df_mapa = pl.DataFrame(filas).to_pandas()

    fig = px.choropleth(
        df_mapa,
        geojson=geojson,
        locations='comunidad',
        featureidkey='properties.name',
        color='valor',
        hover_name='comunidad',
        animation_frame='fecha',
        color_continuous_scale='RdYlGn',
        range_color=[-5, 15],
        title='IPV Variación anual por Comunidad Autónoma (2018-2024)'
    )

    fig.update_geos(fitbounds="locations", visible=False)
    fig.write_html("ipv_espanya.html")

def graficoHeatmapEstacional(dfs):
    df = dfs['data_ipv'].filter(pl.col('Id_ipv') == 3)
    
    df_pivot = df.to_pandas()
    df_pivot['Trimestre'] = df_pivot['FK_Periodo'].apply(lambda x: f"T{x-18}")
    
    pivot = df_pivot.pivot_table(index='Anyo', columns='Trimestre', values='Valor')

    fig = px.imshow(
        pivot,
        labels=dict(x="Trimestre", y="Año", color="Var. Anual %"),
        x=pivot.columns,
        y=pivot.index,
        color_continuous_scale='YlOrRd',
        title='Intensidad de Subida de Precios (IPV) por Trimestre y Año'
    )
    
    fig.update_layout(xaxis_nticks=4)
    fig.write_html("ipv_heatmap.html")

def graficoRankingCCAA(dfs):
    ccaa_nombres = dfs['ipv'].filter(
        pl.col('Nombre').str.contains('General. Índice')
    ).select(['id', 'Nombre'])

    resultados = []
    for row in ccaa_nombres.iter_rows(named=True):
        nombre_limpio = row['Nombre'].split('.')[0].strip()
        
        df_ccaa = dfs['data_ipv'].filter(
            (pl.col('Id_ipv') == row['id']) &
            (pl.col('Fecha') >= datetime(2018, 1, 1)) &
            (pl.col('Fecha') <= datetime(2024, 12, 31))
        ).sort('Fecha')

        if len(df_ccaa) > 1:
            inicio = df_ccaa['Valor'][0]
            fin = df_ccaa['Valor'][-1]
            
            crecimiento = ((fin - inicio) / inicio) * 100
            
            resultados.append({
                'Comunidad': nombre_limpio,
                'Crecimiento %': round(crecimiento, 2)
            })

    df_ranking = pl.DataFrame(resultados).sort('Crecimiento %', descending=True).to_pandas()

    fig = px.bar(
        df_ranking,
        x='Crecimiento %',
        y='Comunidad',
        orientation='h',
        color='Crecimiento %',
        color_continuous_scale='Reds',
        title='¿Dónde ha subido más la vivienda? Crecimiento total acumulado (2018-2024)',
        labels={'Crecimiento %': 'Incremento porcentual total'}
    )

    fig.update_layout(yaxis={'categoryorder':'total ascending'}, template='plotly_white')
    fig.write_html("ranking_ccaa_crecimiento.html")

if __name__ == "__main__":
    datos = conexionBBDD_SSH()
    
                                                # Verificando podemos ver que no tenemos datos nulos, 
    datos_limpiados = verificarDatos(datos)     # además de qestar bien formateados y estructurados ha excepción de las fechas
                                                # para hacer unos gráficos con plotly
    
    graficoIPCeIPV(datos_limpiados)
    graficoIPVEspanya(datos_limpiados)
    graficoHeatmapEstacional(datos_limpiados)
    graficoRankingCCAA(datos_limpiados)