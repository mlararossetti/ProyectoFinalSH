from datetime import datetime
import io
import pandas as pd
import numpy as np
from google.cloud import storage
import gc
from sklearn.linear_model import LinearRegression # type: ignore
import re
from pandas.tseries.offsets import MonthEnd


def process_taxi_data(bucket_name, year_month):
    
#///////////////////////////////////////////////////////////////////////////////////////
    # Cliente de Cloud Storage
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    # Construir los nombres de los archivos en función del año y mes extraídos
    files_to_download = {
        "yellow": f"TLC Trip Record Data/yellow_tripdata_{year_month}.parquet",
        "green": f"TLC Trip Record Data/green_tripdata_{year_month}.parquet",
        "fhvhv": f"TLC Trip Record Data/fhvhv_tripdata_{year_month}.parquet",
        "fhv": f"TLC Trip Record Data/fhv_tripdata__{year_month}.parquet"
    }
    # Ruta local temporal para almacenar archivos descargados
    local_file_paths = {key: f"/tmp/{key}" for key in files_to_download.keys()}
    
    # Descargar archivos de datos desde el bucket
    for key, blob_name in files_to_download.items():
        blob = bucket.blob(blob_name)
        try:
            blob.download_to_filename(local_file_paths[key])
            print(f"Archivo {blob_name} descargado exitosamente.")
        except Exception as e:
            print(f"Error al descargar el archivo {blob_name}: {e}")
            return

#///////////////////////////////////////////////////////////////////////////////////////
 
    # Cargar los DataFrames
    df_YT = pd.read_parquet(local_file_paths["yellow"])
    df_GT = pd.read_parquet(local_file_paths["green"])
    df_FHVHV = pd.read_parquet(local_file_paths["fhvhv"])
    df_FHV = pd.read_parquet(local_file_paths["fhv"])
    
    # Realizar todas las transformaciones de datos de ETL
        # Eliminar datos duplicados
    df_YT = df_YT.drop_duplicates()
    df_GT = df_GT.drop_duplicates()
    df_FHVHV = df_FHVHV.drop_duplicates()
    df_FHV = df_FHV.drop_duplicates()

    # Se renombran las columnas de cada DF
    df_YT = df_YT.rename(columns={
        'tpep_pickup_datetime': 'pickup_datetime',
        'tpep_dropoff_datetime': 'dropoff_datetime',
        'PULocationID': 'pickup_location_id',
        'DOLocationID': 'dropoff_location_id'
    })

    df_GT = df_GT.rename(columns={
        'lpep_pickup_datetime': 'pickup_datetime',
        'lpep_dropoff_datetime': 'dropoff_datetime',
        'PULocationID': 'pickup_location_id',
        'DOLocationID': 'dropoff_location_id'
    })

    df_FHVHV = df_FHVHV.rename(columns={
        'PULocationID': 'pickup_location_id',
        'DOLocationID': 'dropoff_location_id',
        'trip_miles': 'trip_distance',
        'base_passenger_fare': 'fare_amount'
    })

    df_FHV = df_FHV.rename(columns={
        'dropOff_datetime': 'dropoff_datetime',
        'PUlocationID': 'pickup_location_id',
        'DOlocationID': 'dropoff_location_id',
        'SR_Flag': 'shared_match_flag'
    })

    # Reemplazo "Y" por True y otros valores por False
    df_FHVHV['shared_request_flag'] = df_FHVHV['shared_request_flag'].map({'Y': True}).fillna(False)
    df_FHVHV['shared_match_flag'] = df_FHVHV['shared_match_flag'].map({'Y': True}).fillna(False)
    df_FHV['shared_match_flag'] = df_FHV['shared_match_flag'].map({1: True}).fillna(False)

    # Se crean las columnas 'shared_request_flag' y 'shared_match_flag' con valores nulos
    df_YT['shared_request_flag'] = np.nan
    df_YT['shared_match_flag'] = np.nan
    df_GT['shared_request_flag'] = np.nan
    df_GT['shared_match_flag'] = np.nan

    # Se crean las columnas 'passenger_count' y 'payment_type' con valores nulos
    df_FHVHV['passenger_count'] = np.nan
    df_FHVHV['payment_type'] = np.nan

    # Se crea la columna 'total_amount' sumando los valores de las columnas indicadas en el dataset df_FHVHV
    df_FHVHV['total_amount'] = (
        df_FHVHV['fare_amount'] +
        df_FHVHV['sales_tax'] +
        df_FHVHV['bcf'] +
        df_FHVHV['tips'] +
        df_FHVHV['tolls']
    )

    # Se crean las columnas 'passenger_count' y 'payment_type' con valores nulos
    df_FHV['passenger_count'] = np.nan
    df_FHV['trip_distance'] = np.nan
    df_FHV['payment_type'] = np.nan
    df_FHV['fare_amount'] = np.nan
    df_FHV['total_amount'] = np.nan
    df_FHV['shared_request_flag'] = np.nan
    df_FHV['congestion_surcharge'] = np.nan

    # Clasificación
    df_YT['industry'] = 'Yellow Taxi'
    df_GT['industry'] = 'Green Taxi'
    df_FHVHV['industry'] = 'FHV - High Volume'
    df_FHV['industry'] = 'FHV - Other'

    # Lista de columnas que se conservan de todos los df
    columnas_a_conservar = [
        'industry',
        'pickup_datetime',
        'dropoff_datetime',
        'pickup_location_id',
        'dropoff_location_id',
        'passenger_count',
        'trip_distance',
        'payment_type',
        'fare_amount',
        'total_amount',
        'congestion_surcharge',
        'shared_request_flag',
        'shared_match_flag'
    ]

    # Elimino las columnas que no necesito.
    df_YT = df_YT.loc[:, columnas_a_conservar]
    df_GT = df_GT.loc[:, columnas_a_conservar]
    df_FHVHV = df_FHVHV.loc[:, columnas_a_conservar]
    df_FHV = df_FHV.loc[:, columnas_a_conservar]

    # Lista de dataframes
    dataframes = [df_YT, df_GT, df_FHVHV, df_FHV]
    # Se concatenean los df con todas las columnas y se reinicia el índice.
    df = pd.concat(dataframes, join='inner', ignore_index=True)

    # Se eliminan los DataFrames originales
    del df_YT, df_GT, df_FHVHV, df_FHV
    # Se llama al recolector de basura para liberar la memoria
    gc.collect()


    # Convierto los tipos de datos
    df['pickup_datetime'] = df['pickup_datetime'].astype('datetime64[ns]')
    df['dropoff_datetime'] = df['dropoff_datetime'].astype('datetime64[ns]')
    df['industry'] = df['industry'].astype('string')
    df['pickup_location_id'] = df['pickup_location_id'].astype('Int64')
    df['dropoff_location_id'] = df['dropoff_location_id'].astype('Int64')
    df['passenger_count'] = df['passenger_count'].astype('Int64')
    df['payment_type'] = df['payment_type'].astype('Int64')
    df['shared_request_flag'] = df['shared_request_flag'].astype('boolean')
    df['shared_match_flag'] = df['shared_match_flag'].astype('boolean')


    # Identificar fechas fuera de rango 
    # Este rango deberá ser variable en función del mes de los archivos levantados para el ETL de carga en la Nube)
    fecha_inicio = datetime.strptime(year_month + "-01", "%Y-%m-%d")
    fecha_fin = fecha_inicio + MonthEnd(0)

    df = df[(df['pickup_datetime'] >= fecha_inicio) & (df['pickup_datetime'] <= fecha_fin)]
    df = df[(df['dropoff_datetime'] >= fecha_inicio) & (df['dropoff_datetime'] <= fecha_fin)]

    #Se reemplazan valores 0 por nulos
    df['passenger_count'] = df['passenger_count'].replace(0, np.nan)

    # Eliminación de outliers por método de Rango Intercuartílico con mínimo en 0.01.
    # Se reemplazan los valores por nulos pero no se eliminan del dataset ya que cuentan para la cantidad de viajes.
    Q1 = df['trip_distance'].quantile(0.25)
    Q3 = df['trip_distance'].quantile(0.75)
    IQR = Q3 - Q1
    df['trip_distance'] = np.where( (df['trip_distance'] < max(0.01,  Q1 - 1.5 * IQR)) | (df['trip_distance'] > Q3 + 1.5 * IQR), np.nan,
        df['trip_distance'])

    # Elimino los registros con nulos en pickup o dropoff
    df_cleaned = df.dropna(subset=['pickup_location_id', 'dropoff_location_id'])

    # Calcuo la distancia promedio por combinación de pickup_location_id y dropoff_location_id
    distancia_promedio = df_cleaned.groupby(['pickup_location_id', 'dropoff_location_id'])['trip_distance'].mean().reset_index()
    distancia_promedio.columns = ['pickup_location_id', 'dropoff_location_id', 'promedio_distancia']

    # Combino el DataFrame original con el DataFrame de distancia promedio
    df = df_cleaned.merge(distancia_promedio, on=['pickup_location_id', 'dropoff_location_id'], how='left')

    # Relleno los valores nulos en trip_distance con la distancia promedio
    df['trip_distance'] = df['trip_distance'].fillna(df['promedio_distancia'])

    # Elimino la columna temporal de promedio de distancia
    df.drop(columns=['promedio_distancia'], inplace=True)

    # Eliminación de outliers por método de Rango Intercuartílico con mínimo en 0.01.
    # Se reemplazan los valores por nulos pero no se eliminan del dataset ya que cuentan para la cantidad de viajes.
    Q1 = df['fare_amount'].quantile(0.25)
    Q3 = df['fare_amount'].quantile(0.75)
    IQR = Q3 - Q1
    df['fare_amount'] = np.where( (df['fare_amount'] < max(0.01,  Q1 - 1.5 * IQR)) | (df['fare_amount'] > Q3 + 1.5 * IQR), np.nan,
        df['fare_amount'])

    # No puede haber valores negativos
    df['total_amount'] = np.where(df['total_amount'] < 0, np.nan, df['total_amount'])

    # Pongo nulo en total_amount si en fare_amount hay nulo
    df.loc[df['fare_amount'].isna(), 'total_amount'] = np.nan

    # Elimino outliers a partir de los residuos de la correlación con fare_amount
    # Elimino los nulos
    df_no_nan = df.dropna(subset=['fare_amount', 'total_amount'])

    # Defino las variables a correlacional
    X = df_no_nan[['fare_amount']]
    y = df_no_nan['total_amount']

    # Ajusto el modelo de regresión lineal
    model = LinearRegression()
    model.fit(X, y)

    # Predigo los valores de 'total_amount'
    predictions = model.predict(X)

    # Calculo los residuos
    residuals = y - predictions

    # Defino un umbral en el percentil 99% para identificar outliers
    threshold = np.percentile(np.abs(residuals), 99.99)

    # Índices donde el residuo supera el threshold
    outlier_indices = df_no_nan.index[np.abs(residuals) > threshold]

    # Pongo nulo cuando se supera el umbral en los índices que superaron el threshold
    df.loc[outlier_indices, 'total_amount'] = np.nan

    # No puede haber valores negativos
    df['congestion_surcharge'] = np.where(df['congestion_surcharge'] < 0, np.nan, df['congestion_surcharge'])

    # Configurar el valor de shared_match_flag basado en passenger_count
    df['shared_match_flag'] = df['passenger_count'].apply(lambda x: True if x > 1 else False)

    # Máscara donde dropoff_datetime es menor que pickup_datetime
    mask = df['dropoff_datetime'] < df['pickup_datetime']
    # Intercambio los valores en esas filas
    df.loc[mask, ['pickup_datetime', 'dropoff_datetime']] = df.loc[mask, ['dropoff_datetime', 'pickup_datetime']].values
    # Recalculo la duración
    df['trip_duration'] = (df['dropoff_datetime'] - df['pickup_datetime']).dt.total_seconds() / 60

    # Se define el límite de valores de tiempo de viaje superiores a al percentil 99%
    Limit = df['trip_duration'].quantile(.999)

    # Calculo la duración media de trip_duration por combinación de pickup y dropoff location
    mean_duration_by_location = (
        df.groupby(['pickup_location_id', 'dropoff_location_id'])['trip_duration']
        .mean()
        .reset_index()
        .rename(columns={'trip_duration': 'mean_trip_duration'})
    )

    # Uno el promedio de duración con el DataFrame original para usarlo en el reemplazo
    df = df.merge(mean_duration_by_location, on=['pickup_location_id', 'dropoff_location_id'], how='left')

    # Reemplazo los valores de dropoff_datetime fuera del límite con pickup_datetime + mean_trip_duration
    df.loc[df['trip_duration'] > Limit, 'dropoff_datetime'] = (
        df['pickup_datetime'] + pd.to_timedelta(df['mean_trip_duration'], unit='s')
    )

    # Elimino la columna auxiliar 'mean_trip_duration'
    df.drop(columns='mean_trip_duration', inplace=True)

    # Recalculo la duración
    df['trip_duration'] = (df['dropoff_datetime'] - df['pickup_datetime']).dt.total_seconds() / 60

    df['date'] = pd.to_datetime(df['pickup_datetime']).dt.date

    
#///////////////////////////////////////////////////////////////////////
# Creamos el campo que vincula los df
    df['date'] = pd.to_datetime(df['year'].astype(str) + '-' + df['month'].astype(str), format='%Y-%m')
    df['date'] = pd.to_datetime(df['date'], errors='coerce')


    # 1. DataFrame de agregaciones por mes, año y industry
    df_by_industry = df.groupby(
        ['date', 'industry']
    ).agg(
        total_trips=('pickup_datetime', 'count'),
        passenger_count=('passenger_count', 'sum'),
        trip_distance=('trip_distance', 'sum'),
        trip_duration=('trip_duration', 'sum'),
        avg_trip_distance=('trip_distance', 'mean'),
        avg_trip_duration=('trip_duration', 'mean'),
        fare_amount=('fare_amount', 'sum'),
        total_amount=('total_amount', 'sum'),
        shared_match_flag=('shared_match_flag', lambda x: (x == True).sum())
    ).reset_index()

    # 2. DataFrame de agregaciones por mes, año y combinación de pickup_location_id y dropoff_location_id
    df_by_location = df.groupby(
        ['date', 'pickup_location_id', 'dropoff_location_id']
    ).agg(
        total_trips=('pickup_datetime', 'count'),
        passenger_count=('passenger_count', 'sum'),
        trip_distance=('trip_distance', 'sum'),
        trip_duration=('trip_duration', 'sum'),
        avg_trip_distance=('trip_distance', 'mean'),
        avg_trip_duration=('trip_duration', 'mean'), 
        fare_amount=('fare_amount', 'sum'),
        total_amount=('total_amount', 'sum'),
        shared_match_flag=('shared_match_flag', lambda x: (x == True).sum())
    ).reset_index()

    # Liberar memoria
    del df
    gc.collect()

    # Redondear las columnas de tipo DECIMAL antes de cargarlas en SQL
    df_by_location['trip_distance'] = df_by_location['trip_distance'].round(2)
    df_by_location['trip_duration'] = df_by_location['trip_duration'].round(2)
    df_by_location['avg_trip_distance'] = df_by_location['avg_trip_distance'].round(2)  # DECIMAL(5, 2)
    df_by_location['avg_trip_duration'] = df_by_location['avg_trip_duration'].round(2)  # DECIMAL(5, 2)


    # Las columnas como 'pickup_location_id', 'dropoff_location_id', 'total_trips', 'passenger_count', y 'shared_match_flag'
    # son de tipo INT y no requieren redondeo:
    df_by_location['pickup_location_id'] = df_by_location['pickup_location_id'].astype('Int64')
    df_by_location['dropoff_location_id'] = df_by_location['dropoff_location_id'].astype('Int64')
    df_by_location['total_trips'] = df_by_location['total_trips'].astype('Int64')
    df_by_location['passenger_count'] = df_by_location['passenger_count'].astype('Int64')
    df_by_location['shared_match_flag'] = df_by_location['shared_match_flag'].astype('Int64')
    df_by_location['fare_amount'] = df_by_location['fare_amount'].astype('Int64')
    df_by_location['total_amount'] = df_by_location['total_amount'].astype('Int64')
   
    print("El ETL Corrió Bien")


# #///////////////////////////////////////////////////////////////////////    
#     # Agregación location
#     try:
#         # Intentar descargar el archivo existente
#         existing_file_by_location = "TLC Trip Record Data/viajes_depurado_by_location.csv"
#         temp_local_by_location = "/tmp/viajes_depurado_by_location.csv"
#         blob2 = bucket.blob(existing_file_by_location)
#         blob2.download_to_filename(temp_local_by_location)
#         print(f"Archivo existente descargado desde {existing_file_by_location}")

#         # Cargar el archivo existente en un DataFrame
#         df_by_location_old = pd.read_csv(temp_local_by_location)
#     except Exception as e:
#         # Si el archivo no existe, crear un DataFrame vacío con las columnas necesarias
#         print(f"Archivo no encontrado en {existing_file_by_location}. Se creará uno nuevo.")

#     # Concatenar el DataFrame existente con el nuevo DataFrame
#     df_by_location_new = pd.concat([df_by_location_old, df_by_location], ignore_index=True)

#     # Guardar el DataFrame actualizado en un archivo temporal local
#     df_by_location_new.to_csv(temp_local_by_location, index=False)

#     # Subir el archivo actualizado al bucket en Cloud Storage
#     blob2.upload_from_filename(temp_local_by_location)
#     print(f"Archivo actualizado guardado en {existing_file_by_location} en Cloud Storage.")

#     # Liberar memoria
#     del df_by_location_old, df_by_location_new
#     gc.collect()


# #///////////////////////////////////////////////////////////////////////    
#     # Agregación industry
#     try:
#         # Intentar descargar el archivo existente
#         existing_file_by_industry = "TLC Trip Record Data/viajes_depurado_by_industry.csv"
#         temp_local_industry = "/tmp/viajes_depurado_by_industry.csv"
#         blob1 = bucket.blob(existing_file_by_industry)
#         blob1.download_to_filename(temp_local_industry)
#         print(f"Archivo existente descargado desde {existing_file_by_industry}")

#         # Cargar el archivo existente en un DataFrame
#         df_by_industry_old= pd.read_csv(temp_local_industry)
#     except Exception as e:
#         # Si el archivo no existe, crear un DataFrame vacío con las columnas necesarias
#         print(f"Archivo no encontrado en {existing_file_by_industry}. Se creará uno nuevo.")

#     # Concatenar el DataFrame existente con el nuevo DataFrame
#     df_by_industry_new = pd.concat([df_by_industry_old, df_by_industry], ignore_index=True)

#     # Guardar el DataFrame actualizado en un archivo temporal local
#     df_by_industry_new.to_csv(temp_local_industry, index=False)

#     # Subir el archivo actualizado al bucket en Cloud Storage
#     blob1.upload_from_filename(temp_local_industry)
#     print(f"Archivo actualizado guardado en {existing_file_by_industry} en Cloud Storage.")

#     # Liberar memoria
#     del df_by_industry_old #, df_by_industry_new
#     gc.collect()


# #///////////////////////////////////////////////////////////////////////

#     # Agregación datos mensuales
#     try:
#         # Intentar descargar el archivo existente
#         existing_file_monthly = "TLC Aggregated Data/tripdata_{year_month}.csv"
#         temp_local_monthl = "/tmp/tripdata_{year_month}.csv"
#         blob3 = bucket.blob(existing_file_monthly)
#         blob3.download_to_filename(temp_local_monthl)
#         print(f"Archivo existente descargado desde {temp_local_monthl}")

#         # Cargar el archivo existente en un DataFrame
#         df = pd.read_csv(temp_local_monthl)
#     except Exception as e:
#         # Si el archivo no existe, crear un DataFrame vacío con las columnas necesarias
#         print(f"Archivo no encontrado en {existing_file_monthly}. Se creará uno nuevo.")


# #///////////////////////////////////////////////////////////////////////
#     # ETL de datos mensuales

#     df.columns = [
#     'date', 'industry', 'trips_per_day', 'farebox_per_day',
#     'unique_drivers', 'unique_vehicles', 'vehicles_per_day',
#     'avg_days_vehicles_on_road', 'avg_hours_per_day_per_vehicle',
#     'avg_days_drivers_on_road', 'avg_hours_per_day_per_driver',
#     'avg_minutes_per_trip', 'percent_of_trips_paid_with_credit_card',
#     'trips_per_day_shared'
# ]

#     # Columnas incuidas
#     columns_to_replace = df.columns.difference(['date', 'industry'])
#     # Reemplazar '-' por '' en las columnas seleccionadas
#     df[columns_to_replace] = df[columns_to_replace].replace({'-':np.nan,',':'','%': ''}, regex=True)

#     df['date'] = pd.to_datetime(df['date'], format='%Y-%m')
#     df['industry'] = df['industry'].astype('category')
#     df['trips_per_day'] = df['trips_per_day'].astype('Int64')
#     df['farebox_per_day'] = df['farebox_per_day'].astype('Int64')
#     df['unique_drivers'] = df['unique_drivers'].astype('Int64')
#     df['unique_vehicles'] = df['unique_vehicles'].astype('Int64')
#     df['vehicles_per_day'] = df['vehicles_per_day'].astype('Int64')
#     df['percent_of_trips_paid_with_credit_card'] = pd.to_numeric(df['percent_of_trips_paid_with_credit_card'], errors='coerce') / 100
#     df['trips_per_day_shared'] = pd.to_numeric(df['trips_per_day_shared'], errors='coerce') 

#     # Reemplazar 'Green' y 'Yellow' para igual al datset diario
#     df['industry'] = df['industry'].replace({'Green': 'Green Taxi', 'Yellow': 'Yellow Taxi'})

#     # Agregar "FHV - Other" a las categorías de la columna 'industry' para reemplazar las que no están en el datset diario  
#     df['industry'] = df['industry'].cat.add_categories('FHV - Other')

#     # Luego, realizar la asignación de las industrias
#     other_industries = ['FHV - Black Car', 'FHV - Livery', 'FHV - Lux Limo']
#     df.loc[df['industry'].isin(other_industries), 'industry'] = 'FHV - Other'

#     # Agrupar por 'month_year' y 'industry', y agregar 'FHV - Other' por mes
#     df_other = df[df['industry'] == 'FHV - Other'].groupby('date').agg({
#         'trips_per_day': 'sum',
#         'farebox_per_day': 'sum',
#         'unique_drivers': 'sum',
#         'unique_vehicles': 'sum',
#         'vehicles_per_day': 'sum',
#         'avg_days_vehicles_on_road': 'mean',
#         'avg_hours_per_day_per_vehicle': 'mean',
#         'avg_days_drivers_on_road': 'mean',
#         'avg_hours_per_day_per_driver': 'mean',
#         'avg_minutes_per_trip': 'mean',
#         'percent_of_trips_paid_with_credit_card': 'mean',
#         'trips_per_day_shared': 'sum'
#     }).reset_index()

#     # Reasignar índices y juntar los DataFrames
#     df_other['industry'] = 'FHV - Other'  # Asegurarse de que la columna 'industry' sea consistente
#     df = pd.concat([df[df['industry'] != 'FHV - Other'], df_other], ignore_index=True)

#     # Acululamos desde el 2021
#     df = df[df['date'] >= '2021-01-01']

# #////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#     # Creamos el campo que vincula los df
#     df_by_industry_new['date'] = pd.to_datetime(df_by_industry_new['year'].astype(str) + '-' + df_by_industry_new['month'].astype(str), format='%Y-%m')
#     df_by_industry_new['date'] = pd.to_datetime(df_by_industry_new['date'], errors='coerce')
    
#     df['date'] = pd.to_datetime(df['date'], errors='coerce')

#     df_total = pd.merge(df,df_by_industry_new, on=['date', 'industry'], how='outer')

# #////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#        # Obtener la cantidad de días en el mes de cada registro
#     df_total['days_in_month'] = df_total['date'].dt.days_in_month
#     # Calcular total_trips como trips_per_day * days_in_month
#     df_total['total_trips'] = df_total['trips_per_day'] * df_total['days_in_month']

#     # Crear el nuevo campo 'farebox_per_day' con valores diferenciados
#     df_total['farebox_per_day'] = np.where(
#         df_total['industry'] == 'FHV - High Volume',
#         df_total['total_amount'] / df_total['days_in_month'],
#         df_total['farebox_per_day']
#     )

#     # Crear el nuevo campo 'total_amount' con valores diferenciados
#     df_total['total_amount'] = np.where(
#         df_total['industry'] == 'FHV - High Volume',
#         df_total['total_amount'],
#         df_total['farebox_per_day'] * df_total['days_in_month']
#     )

#     # Lo mismo pero para cantidad de viajes compartidos
#     df_total['shared_match_flag'] = np.where(
#         df_total['industry'] == 'FHV - High Volume',
#         df_total['trips_per_day_shared'] * df_total['days_in_month'],
#         df_total['shared_match_flag']
#     )

#     # Lo mismo pero para cantidad de viajes compartidos
#     df_total['trips_per_day_shared'] = np.where(
#         df_total['industry'] == 'FHV - High Volume',
#         df_total['trips_per_day_shared'],
#         df_total['shared_match_flag'] / df_total['days_in_month']
#     )

#     df_total['farebox_per_day_per_distance']=df_total['farebox_per_day']/df_total['avg_trip_distance']

#     df_total['total_co2_emission'] = df_total['avg_trip_distance'] * df_total['total_trips'] * 400 / 1000000


#     # Redondear las columnas de tipo DECIMAL antes de cargarlas en SQL
#     df_total['farebox_per_day'] = df_total['farebox_per_day'].round(2)
#     df_total['avg_days_vehicles_on_road'] = df_total['avg_days_vehicles_on_road'].round(2)
#     df_total['avg_hours_per_day_per_vehicle'] = df_total['avg_hours_per_day_per_vehicle'].round(2)
#     df_total['avg_days_drivers_on_road'] = df_total['avg_days_drivers_on_road'].round(2)
#     df_total['avg_hours_per_day_per_driver'] = df_total['avg_hours_per_day_per_driver'].round(2)
#     df_total['percent_of_trips_paid_with_credit_card'] = df_total['percent_of_trips_paid_with_credit_card'].round(2)
#     df_total['avg_trip_distance'] = df_total['avg_trip_distance'].round(2)
#     df_total['avg_trip_duration'] = df_total['avg_trip_duration'].round(2)
#     df_total['total_amount'] = df_total['total_amount'].round(2)
#     df_total['farebox_per_day_per_distance'] = df_total['farebox_per_day_per_distance'].round(4)
#     df_total['total_co2_emission'] = df_total['total_co2_emission'].round(4)

#     # Empezamos a trabajar con el dataset eliminando columnas o componiendo datos
#     df_total = df_total.drop(columns=['year', 'month','trip_distance','trip_duration','fare_amount','avg_minutes_per_trip'])
#     df_total['farebox_per_day'] = df_total['farebox_per_day'].replace(0, np.nan) 
#     df_total['trips_per_day_shared'] = df_total['trips_per_day_shared'].replace(0, np.nan) 
#     df_total['passenger_count'] = df_total['passenger_count'].replace(0, np.nan) 
#     df_total['total_amount'] = df_total['total_amount'].replace(0, np.nan) 
#     df_total['shared_match_flag'] = df_total['shared_match_flag'].replace(0, np.nan)
#     df_total['farebox_per_day_per_distance'] = df_total['farebox_per_day_per_distance'].replace(0, np.nan)

#     # Eliminar columnas duplicadas
#     df_total = df_total.loc[:, ~df_total.columns.duplicated()]

#     temp_local_path = "/tmp/merged_taxi_data.csv"
#     # Guardar el DataFrame actualizado en un archivo temporal local
#     df_total.to_csv(temp_local_path, index=False)

#     # Subir el archivo actualizado al bucket en Cloud Storage
#     blob2.upload_from_filename(temp_local_path)
#     print(f"ETL Finalizado. Archivo actualizado guardado en {temp_local_path} en Cloud Storage.")
