import pandas as pd 
import os
import warnings 
import numpy as np
warnings.filterwarnings('ignore')

_CSV_PATH = './data/csv'
_PARQUET_PATH = './data'

# Concateno csv de producción en un archivo parquet. 
# Esto debería correrse cada vez que la carpeta de data/csv se actualiza
data_files = os.listdir(_CSV_PATH)
df = pd.concat((pd.read_csv(_CSV_PATH + '/' + filename) for filename in data_files))

# Creo columnas
df['fecha_data'] = pd.to_datetime(df['fecha_data'],yearfirst=True)
df['dias'] = df['fecha_data'].dt.day
df['Th bbl/d'] = df['prod_pet'] / df['dias'] * 6.2898 / 1000 
df['Mm3/d'] = df['prod_gas'] / df['dias'] / 1000
df['Th boe/d'] = df['Th bbl/d'] + df['Mm3/d'] * 6.29

# Filtro Gasífero y Petrolífero
df = df.query("tipopozo in ('Gasífero','Petrolífero')")

# Renombro columnas
df.rename(columns={'fecha_data':'Date'},inplace=True)

# Resuelvo datos NaN y errores
df['sub_tipo_recurso'].fillna('CONVENCIONAL',inplace=True)
df['idempresa'] = df['idempresa'].astype(str)

# Encuentro primer mes para curvas de producción
df_primer_mes = pd.DataFrame(df.groupby(by='idpozo')['Date'].min()).reset_index()
df_primer_mes.rename(columns={'Date':'primer_mes'},inplace=True)
df = df.merge(df_primer_mes,on='idpozo',how='left')
df['anio_inicio'] = df['primer_mes'].apply(lambda x: x.year)
df['mes_produccion'] = ((df['Date'] - df['primer_mes'])/np.timedelta64(1,'D')/30).round() + 1 

# Creo dataframe con nuevos pozos puestos en producción
df_new_wells = df.sort_values(by='Date',
                              ascending=True
                ).drop_duplicates(subset=['idpozo'],
                                  keep='first')

# Creo dataframe de producción
df_prod_resource_basin = df.groupby(['sub_tipo_recurso','Date','cuenca','empresa'])[['Th bbl/d','Mm3/d','Th boe/d']].sum().reset_index()

# Creo dataframe de curvas de producción
df_curve = df.groupby(by=['anio_inicio','mes_produccion','sub_tipo_recurso','tipopozo','cuenca','areapermisoconcesion','empresa']).aggregate({'Th boe/d':'sum','sigla':'count'}).reset_index()
df_curve = df_curve[df_curve['anio_inicio'] > 2006]


# Exporto a parquet
df_new_wells.to_parquet(f'{_PARQUET_PATH}/database_new_wells.parquet')
df_prod_resource_basin.to_parquet(f'{_PARQUET_PATH}/database_prod_resource_basin.parquet')
df_curve.to_parquet(f'{_PARQUET_PATH}/database_curve.parquet')
