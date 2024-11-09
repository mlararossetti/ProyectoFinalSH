import os
import urllib.request
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
import csv
import logging
from google.cloud import storage
import time
from io import BytesIO
from datetime import datetime
from pandas.tseries.offsets import MonthEnd

import pandas as pd
import numpy as np
import gc
from sklearn.linear_model import LinearRegression
import warnings 
warnings.filterwarnings("ignore")

def ETL_Viajes_Diarios (output_folder,year_month):
        
    # Yellow Taxi Tripdata
    df_YT = pd.read_parquet(output_folder + "\\yellow_tripdata_" + year_month + ".parquet")
    # Green Taxi Tripdata
    df_GT = pd.read_parquet(output_folder + "\\green_tripdata_" + year_month + ".parquet")
    # FHV - High Volume
    df_FHVHV = pd.read_parquet(output_folder + "\\fhvhv_tripdata_" + year_month + ".parquet")
    # FHV - Other
    df_FHV = pd.read_parquet(output_folder + "\\fhv_tripdata_" + year_month + ".parquet")

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
    # fecha_inicio = '2020-12-01'
    # fecha_fin = '2021-02-28'
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
    duration_count_99 = df[df['trip_duration'] > Limit].groupby('industry').size().reset_index(name='count')

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

    df['year'] = df['pickup_datetime'].dt.year
    df['month'] = df['pickup_datetime'].dt.month
    df['day_of_week'] = df['pickup_datetime'].dt.day_name()
    df['hour'] = df['pickup_datetime'].dt.hour
    df['day_of_week_num'] = df['pickup_datetime'].dt.dayofweek #(0=Lunes, ..., 6=Domingo)
    df['date'] = pd.to_datetime(df['pickup_datetime']).dt.date

    # Cargamos el dataset de feriados y convertimos la columna 'date' a solo fecha
    df_feriados = pd.read_csv(output_folder + "\\feriados_nacionales_2021_2024.csv")
    df_feriados['date'] = pd.to_datetime(df_feriados['date']).dt.date

    # Realizamos el merge para identificar los días feriados
    df = df.merge(df_feriados[['date','name']], how='left', left_on='date', right_on='date')

    # Creamos la columna 'is_holiday' que marca True si es feriado y False en caso contrario
    df['is_holiday'] = df['name'].notna()

    # Creamos la columna 'working_day'
    # Marcamos como 'No Laborable' (False) los días feriados o los fines de semana (sábado y domingo)
    df['working_day'] = ~((df['is_holiday']) | (df['day_of_week_num'] >= 5))

    # Opcional: Convertimos el campo 'working_day' a 'Laborable' o 'No Laborable' para mejor comprensión
    df['working_day'] = df['working_day'].map({True: 'Laborable', False: 'No Laborable'})

    # Eliminamos columnas temporales si ya no son necesarias
    df.drop(columns=['date', 'is_holiday'], inplace=True)


#/////////////////////////////////////////////////////////////////////////////////////////////////////////////
    # 1. DataFrame de agregaciones por mes, año y industry
    df_by_industry = df.groupby(
        ['year', 'month', 'industry']
    ).agg(
        total_trips=('pickup_datetime', 'count'),
        passenger_count=('passenger_count', 'sum'),
        trip_distance=('trip_distance', 'sum'),
        trip_duration=('trip_duration', 'sum'),
        avg_trip_distance=('trip_distance', 'mean'),
        avg_trip_duration=('trip_duration', 'mean'),
        fare_amount=('fare_amount', 'sum'),
        total_amount=('total_amount', 'sum'),
        shared_requests=('shared_match_flag', lambda x: (x == True).sum())
    ).reset_index()

    # 2. DataFrame de agregaciones por mes, año y combinación de pickup_location_id y dropoff_location_id
    df_by_location = df.groupby(
        ['year', 'month', 'pickup_location_id', 'dropoff_location_id']
    ).agg(
        total_trips=('pickup_datetime', 'count'),
        passenger_count=('passenger_count', 'sum'),
        trip_distance=('trip_distance', 'sum'),
        trip_duration=('trip_duration', 'sum'),
        avg_trip_distance=('trip_distance', 'mean'),
        avg_trip_duration=('trip_duration', 'mean'), 
        fare_amount=('fare_amount', 'sum'),
        total_amount=('total_amount', 'sum'),
        shared_requests=('shared_match_flag', lambda x: (x == True).sum())
    ).reset_index()


    # Guarda los datos consolidados en csv
    file_industry = output_folder + "viajes_depurado_by_industry.csv"    
    file_location =output_folder + "viajes_depurado_by_location.csv"

    # Función para anexar o crear archivo CSV
    def append_to_csv(file_path, new_data):
        # Si el archivo existe, cargar y anexar datos; si no, crear uno nuevo
        if os.path.exists(file_path):
            existing_data = pd.read_csv(file_path)
            combined_data = pd.concat([existing_data, new_data], ignore_index=True)
        else:
            combined_data = new_data
        
        # Guardar el DataFrame resultante en el archivo CSV
        combined_data.to_csv(file_path, index=False)

    # Anexar los datos para cada archivo
    append_to_csv(file_industry, df_by_industry)
    append_to_csv(file_location, df_by_location)

    # Guarda el DataFrame en un archivo parquet
    df.to_parquet(output_folder + "\\viajes_depurado_" + year_month + ".parquet", engine='pyarrow', index=False)

    print ("ETL Procesado OK")

    # Función para leer la última fecha registrada y calcular el siguiente mes
def get_start_date_from_csv(file_path):
    try:
        with open(file_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            last_row = list(reader)[-1]  # Obtener la última fila
            last_date = datetime.strptime(last_row[0], "%d/%m/%Y")  # Parsear la fecha en formato "DD/MM/YYYY"
            return last_date + relativedelta(months=1)  # Retornar el mes siguiente
    except Exception as e:
        logging.error(f"Error leyendo {file_path}: {e}")
        return datetime(2021, 1, 1)  # Valor predeterminado si no existe el archivo o falla la lectura


import time
import csv
from datetime import datetime
from dateutil.relativedelta import relativedelta
from io import BytesIO

# Nombre del bucket en GCS
BUCKET_NAME = 'henry-taxis'

# Función para verificar y descargar archivos .parquet y subirlos a GCS directamente
def download_and_upload_to_gcs(base_urls, start_date, csv_url, fechas_csv, retries=3, delay=5):
    """
    Descargar archivos .parquet y CSV y subirlos directamente a Google Cloud Storage.
    """
    # Para cada fecha desde el inicio hasta el mes actual:
    end_date = datetime.now()
    current_date = start_date

    while current_date <= end_date:
        year_month = current_date.strftime("%Y-%m")  # Formato año-mes
        all_files_downloaded = True  # Bandera para verificar descarga de todos los archivos .parquet

        # Se recorren todas las URL de los archivos parquet.
        for dataset_type, base_url in base_urls.items():
            
            # Construir la URL y el nombre de archivo de destino
            url = base_url.format(year_month)
            file_name = f"{dataset_type}_tripdata_{year_month}.parquet"
            blob_name = f"parquet/{file_name}"

            # Intentar descargar el archivo si no existe en GCS
            success = download_and_upload_file(url, BUCKET_NAME, blob_name, retries, delay)
            if not success:
                all_files_downloaded = False  # Marcar como falso si falla alguna descarga

        
        # Si logró descargar los archivos .parquet del mes:
        if all_files_downloaded:

            # Descarga el archivo CSV mensual y súbelo directamente a GCS
            csv_blob_name = f"csv/tripdata_{year_month}.csv"
            download_and_upload_file(csv_url, BUCKET_NAME, csv_blob_name, retries, delay)

            # Realiza el ETL de los archivos descargados
            ETL_Viajes_Diarios(year_month)

            # Guardar la fecha en Fechas_Archivos_Levantados.csv
            save_date_to_csv(current_date, fechas_csv)

        # Avanzar al siguiente mes
        current_date += relativedelta(months=1)

# Función para descargar y subir un archivo directamente a Google Cloud Storage
def download_file(url, bucket_name, blob_name, retries=3, delay=5):
    """
    Descargar un archivo y subirlo directamente a Google Cloud Storage.
    """
    for attempt in range(1, retries + 1):
        try:
            # Descargar el archivo en memoria
            with urllib.request.urlopen(url) as response:
                file_data = response.read()  # Leer el contenido del archivo
            
            # Subir el archivo a GCS desde la memoria
            upload_to_gcs(bucket_name, file_data, blob_name)
            print(f"Archivo {url} subido a {bucket_name}/{blob_name}.")
            return True  # Éxito en la descarga y subida

        except Exception as e:
            if attempt == retries:
                error_type = type(e).__name__
                logging.error(f"Error {error_type} al descargar o subir {url}: {e}")
            else:
                time.sleep(delay)  # Esperar antes de intentar de nuevo
    return False  # Falla después de todos los intentos

# Función para subir un archivo a Google Cloud Storage desde memoria
def upload_to_gcs(bucket_name, file_data, blob_name):
    """
    Subir un archivo desde memoria a Google Cloud Storage.
    """
    storage_client = storage.Client()  # Cliente para interactuar con GCS
    bucket = storage_client.bucket(bucket_name)  # Obtener el bucket
    blob = bucket.blob(blob_name)  # Crear un blob (archivo) en el bucket

    try:
        # Subir el archivo a GCS desde la memoria (BytesIO)
        blob.upload_from_string(file_data)
        print(f"Archivo subido a {bucket_name}/{blob_name}.")
    except Exception as e:
        logging.error(f"Error subiendo archivo a GCS: {e}")

# Función para guardar la fecha de descarga en el archivo CSV
def save_date_to_csv(date, file_path):
    try:
        with open(file_path, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([date.strftime("%d/%m/%Y")])  # Guardar la fecha en formato "DD/MM/YYYY"
    except Exception as e:
        logging.error(f"Error guardando fecha en {file_path}: {e}")
