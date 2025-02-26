import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta
import matplotlib.ticker as ticker  
import numpy as np
# No usadas
import time 
import gc

#======================================================================================
# Obtener el nombre de usuario local del sistema
nombre_usuario = os.getlogin()

# CARPETA DONDE SE GUARDA EL PLOT PARA SUBIR A LA WEB
RUTA_GUARDADO = f'C:/Users/{nombre_usuario}/OneDrive/LAST_PLOT_EFM' 

# DEFINIR RESOLUCION TEMPORAL Y SHOW DEL PLOT 
RT = "60"
SHOW_FIGURE = False

#======================================================================================
# TRATAMIENTO DE MEDIA MENSUAL PG
# Asignar manualmente los valores de MEDIA_MES
MEDIA_MES = pd.DataFrame({
    'H': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23],
    'DESVEST': [12, 12, 12, 13, 13, 14, 18, 25, 31, 32, 31, 29, 29, 31, 42, 50, 44, 27, 19, 18, 16, 15, 14, 13],
    'PG': [29, 29, 28, 27, 26, 28, 37, 52, 72, 92, 105, 105, 105, 105, 101, 93, 76, 67, 64, 53, 42, 35, 31, 30]
})

MEDIA_MES['H'] = MEDIA_MES['H'].shift(-5)
valores = [0, 1, 2, 3, 4]

for i, row in MEDIA_MES.iterrows():
    # Si el valor de la columna 'hora' es NaN
    if pd.isnull(row['H']):
        # Reemplaza el valor NaN por el primer elemento de la lista 'valores'
        MEDIA_MES.at[i, 'H'] = valores[0]
        # Elimina el primer elemento de la lista 'valores'
        valores.pop(0)

MEDIA_MES = MEDIA_MES.sort_values(by='H')
MEDIA_MES['H'] = MEDIA_MES['H'] + 0.5
y2 = MEDIA_MES['PG']
x2 = MEDIA_MES['H']
y_std = MEDIA_MES['DESVEST']  # Utilizar los valores de DESVEST como desviación estándar
#======================================================================================
# LECTURA DEL CSV DESDE GITHUB
url = "https://raw.githubusercontent.com/rr2021/pg_ica_csv/main/ICA-LAST.efm"

# Obtener la fecha actual en UTC en formato MMDDYYYY y luego convertirlo a DD/MM/YYYY
name = datetime.utcnow().strftime('%m%d%Y')  # Formato MMDDYYYY
name = datetime.strptime(name, '%m%d%Y').strftime('%d/%m/%Y')  # Conversión a DD/MM/YYYY

# Lectura del CSV con transformación directa de columnas
df = pd.read_csv(
    url, 
    delimiter=',', 
    names=["H", "PG"], 
    skiprows=0, 
    usecols=(0, 1),
    parse_dates=["H"],  # Convertir 'H' a datetime directamente
    infer_datetime_format=True  # Optimización en el parsing
)

# Transformación de la columna 'PG'
df['PG'] = (df['PG'] + 0.083670597) / 0.0048953412

# Crear columna 'DATETIME' combinando 'name' con la hora de 'H'
df['DATETIME'] = pd.to_datetime(datetime.strptime(name, '%d/%m/%Y').strftime('%Y-%m-%d') + ' ' + df['H'].dt.strftime('%H:%M:%S'))

# Establecer 'DATETIME' como índice
df.set_index('DATETIME', inplace=True)


#======================================================================================
# RESAMPLE Y PROCESAMIENTO DE DATOS
df2 = df.resample(f"{RT}S").mean().ffill()

# Último valor de PG
ultimo_valor = round(df2['PG'].iloc[-1], 0).astype(int)

# Convertir 'H' a string y extraer valores en horas decimales
H = df2.index.strftime('%H:%M:%S')
hourday = np.array([int(h[:2]) + int(h[3:5]) / 60 + int(h[6:]) / 3600 for h in H])

# DEFINICION DE DATOS DE PG
x, y = hourday, df2['PG']

# OBTENER HORA LOCAL Y HORA EJE
now_utc = datetime.utcnow()
HORA_LOCAL = (now_utc - timedelta(hours=5)).strftime("%H:%M:%S")

HORA_EJE = now_utc.hour + now_utc.minute / 60 + now_utc.second / 3600

#======================================================================================
# PLOTEO
fig, ax = plt.subplots(figsize=(6, 4.5))
ax.plot(x, y, linewidth=0.75, color="k", label="Valor Actual: " + str(ultimo_valor) + " V/m")

ax.set_title("Fecha: " + name + "     Hora Local: " + HORA_LOCAL + "     RT: " + RT + "s", 
             loc="center", y=1.12, pad=-20)
plt.ylabel('PG (V/m)')
plt.xlabel('Hora (UT): ' + now_utc.strftime("%H:%M:%S"))

#==================================================================
# GRAFICO DE CURVA ESTANDAR
ax.plot(x2, y2, 'r', label="Curva estándar", linewidth=1, linestyle="--", alpha=0.6)
# BARRAS DE ERROR:
ax.fill_between(x2, y2 - y_std, y2 + y_std, color='r', alpha=0.15)  # Agregar las barras de error al gráfico 
#==================================================================

fig.suptitle("Campo Eléctrico en el CIEASEST - UNICA - ICA", 
             fontsize=14, y=1.00)

plt.grid(visible=True, axis='both', color='k', linestyle='--', linewidth=0.5, alpha=0.3)

ax.set_xlim([0, 24])
ax.set_xticks(range(0, 25, 4))

# Configuración de ticks mayores y menores
ax.xaxis.set_major_locator(ticker.MultipleLocator(4))  # Ticks mayores cada 4 horas
ax.xaxis.set_minor_locator(ticker.MultipleLocator(1))  # Ticks menores cada 1 hora
ax.yaxis.set_major_locator(ticker.AutoLocator())       # Ticks mayores automáticos
ax.yaxis.set_minor_locator(ticker.AutoMinorLocator(4)) # Ticks menores entre los mayores

ax.legend(loc='best')

# OUTPUT
plt.savefig(os.path.join(RUTA_GUARDADO, 'PG_ICA_SWP_GRUPO_3.jpg'), dpi=300, bbox_inches='tight')

if SHOW_FIGURE:
    plt.show()
else:
    plt.close(fig)
