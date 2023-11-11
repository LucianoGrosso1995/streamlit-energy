import pandas as pd 
import os

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
df['Th boe/d'] = df['Th bbl/d'] + df['Mm3/d'] * 6.29 / 1000

# Renombro columnas
df.rename(columns={'fecha_data':'Date'},inplace=True)

# Resuelvo datos NaN y errores
df['sub_tipo_recurso'].fillna('CONVENCIONAL',inplace=True)
df['idempresa'] = df['idempresa'].astype(str)

# Creo dataframe con nuevos pozos puestos en producción
df_new_wells = df.sort_values(by='Date',
                              ascending=True
                ).drop_duplicates(subset=['idpozo'],
                                  keep='first')

df_prod_resource_basin = df.groupby(['sub_tipo_recurso','Date','cuenca','empresa'])[['Th bbl/d','Mm3/d','Th boe/d']].sum().reset_index()

# Exporto a parquet
df_new_wells.to_parquet(f'{_PARQUET_PATH}/database_new_wells.parquet')
df_prod_resource_basin.to_parquet(f'{_PARQUET_PATH}/database_prod_resource_basin.parquet')