import logging
from google.cloud import storage
import time
from datetime import datetime
import urllib.request
import csv
from dateutil.relativedelta import relativedelta

from functions_ETL import ETL_Viajes_Diarios


# import time
# import csv
# from datetime import datetime
# from dateutil.relativedelta import relativedelta
# from io import BytesIO


log_file = '/tmp/error_log.log'  # Archivo local temporal para logs
logging.basicConfig(filename=log_file, level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')


# Función para subir los logs a GCS
def upload_logs_to_gcs(log_file, bucket_name, destination_blob_name):
    """Sube un archivo de log desde el sistema local a un bucket de GCS."""
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(log_file)
    print(f"Log file uploaded to {bucket_name}/{destination_blob_name}")



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


# Función para descargar y subir un archivo directamente a Google Cloud Storage
def download_and_upload_file(url, bucket_name, blob_name, retries, delay):
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



## //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# Función para verificar y descargar archivos .parquet y subirlos a GCS directamente

def download_and_upload_to_gcs(base_urls, output_folder, start_date, csv_url, fechas_csv, BUCKET_NAME, retries=3, delay=5):
    
    print("Llegó al download_and_upload_to_gcs")


    """
    Descargar archivos .parquet y CSV y subirlos directamente a Google Cloud Storage.
    """
    # Para cada fecha desde el inicio hasta el mes actual:
    end_date = datetime.now()   # PENDIENTE DE CORREGIR
    current_date = start_date

    while current_date <= end_date:
        year_month = current_date.strftime("%Y-%m")  # Formato año-mes
        all_files_downloaded = True  # Bandera para verificar descarga de todos los archivos .parquet

        # Se recorren todas las URL de los archivos parquet.
        for dataset_type, base_url in base_urls.items():
            
            # Construir la URL y el nombre de archivo de destino
            url = base_url.format(year_month)
            file_name = f"{dataset_type}_tripdata_{year_month}.parquet"
            blob_name = f"TLC Trip Record Data/{file_name}"



            # Intentar descargar el archivo si no existe en GCS
            success = download_and_upload_file(url, BUCKET_NAME, blob_name, retries, delay)
            if not success:
                print("Fallo la descarga")
                all_files_downloaded = False  # Marcar como falso si falla alguna descarga

        
        # Si logró descargar los archivos .parquet del mes:
        if all_files_downloaded:
            print("Bajó todos los archivos.")

            # Descarga el archivo CSV mensual y súbelo directamente a GCS
            csv_blob_name = f"TLC Aggregated Data/tripdata_{year_month}.csv"
            download_and_upload_file(csv_url, BUCKET_NAME, csv_blob_name, retries, delay)

            # Realiza el ETL de los archivos descargados
            ETL_Viajes_Diarios(output_folder, year_month)

            # Guardar la fecha en Fechas_Archivos_Levantados.csv
            save_date_to_csv(current_date, fechas_csv)

        # Avanzar al siguiente mes
        current_date += relativedelta(months=1)
