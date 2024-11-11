import logging
from google.cloud import storage
import time
from datetime import datetime
import urllib.request
import csv
from dateutil.relativedelta import relativedelta
from io import StringIO
from functions_ETL import process_taxi_data


#log_file = '/tmp/error_log.log'  # Archivo local temporal para logs
#logging.basicConfig(filename=log_file, level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')


## //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# Función para verificar y descargar archivos .parquet y subirlos a GCS directamente
def download_and_upload_to_gcs(base_urls, start_date, monthly_url, fechas_csv, bucket_name, retries=3, delay=5):
    
    print("Llegó al download_and_upload_to_gcs")

    """
    Descargar archivos .parquet y CSV y subirlos directamente a Google Cloud Storage.
    """
    year_month = start_date.strftime("%Y-%m")  # Formato año-mes
    all_files_downloaded = True  # Bandera para verificar descarga de todos los archivos .parquet

    # Se recorren todas las URL de los archivos parquet.
    for dataset_type, base_url in base_urls.items():
            
        # Construir la URL y el nombre de archivo de destino
        url = base_url.format(year_month)
        file_name = f"{dataset_type}_tripdata_{year_month}.parquet"
        blob_name = f"TLC Trip Record Data/{file_name}"

        # Intentar descargar el archivo si no existe en GCS
        success = download_and_upload_file(url, bucket_name, blob_name, retries, delay)
        if not success:
            print("Fallo la descarga")
            all_files_downloaded = False
            break # Marcar como falso si falla alguna descarga

    
    # Si logró descargar los archivos .parquet del mes:
    if all_files_downloaded:
        print("Bajó todos los archivos Parquet.")
        
        # Descarga el archivo CSV mensual y súbelo directamente a GCS
        csv_blob_name = f"TLC Aggregated Data/tripdata_{year_month}.csv"
        download_and_upload_file(monthly_url, bucket_name, csv_blob_name, retries, delay)

        # Realiza el ETL de los archivos descargados
        process_taxi_data(bucket_name, year_month)

        # Guardar la fecha en Fechas_Archivos_Levantados.csv
        save_date_to_csv(start_date,bucket_name, fechas_csv)


## //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

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


def save_date_to_csv(date, bucket_name, file_path):
    # Crear cliente de GCS
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(file_path)

    try:
        # Descargar el archivo actual en memoria (si existe)
        if blob.exists():
            existing_data = blob.download_as_text()
            rows = existing_data.splitlines()
        else:
            rows = []

        # Crear un nuevo contenido de archivo con la nueva fecha añadida
        output = StringIO()
        writer = csv.writer(output)
        for row in csv.reader(rows):  # Copiar filas existentes
            writer.writerow(row)
        writer.writerow([date.strftime("%d/%m/%Y")])  # Añadir la nueva fecha

        # Subir el archivo actualizado a GCS
        blob.upload_from_string(output.getvalue(), content_type="text/csv")
        print(f"Fecha {date.strftime('%d/%m/%Y')} guardada exitosamente en {file_path}")
    except Exception as e:
        logging.error(f"Error guardando fecha en gs://{bucket_name}/{file_path}: {e}")



## //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#Funcion para obtener la fecha del archivo del bucket
def get_start_date_from_csv(bucket_name, fechas_csv):
    # Crear cliente de GCS
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(fechas_csv)

    # Descargar el contenido del archivo
    try:
        data = blob.download_as_text()
        reader = csv.reader(data.splitlines())
        last_row = list(reader)[-1]  # Obtener la última fila

        # Parsear la fecha en formato "DD/MM/YYYY"
        last_date = datetime.strptime(last_row[0], "%d/%m/%Y")
        return last_date + relativedelta(months=1)  # Retornar el mes siguiente
    except Exception as e:
        print("No se encontró la fecha o hubo un error al leer el archivo.")
        logging.error(f"Error leyendo gs://{bucket_name}/{fechas_csv}: {e}")
        raise ValueError(f"Error al leer la fecha del archivo {fechas_csv}: {e}")
    

# Función para subir los logs a GCS
# def upload_logs_to_gcs(log_file, bucket_name, destination_blob_name):
#     """Sube un archivo de log desde el sistema local a un bucket de GCS."""
#     client = storage.Client()
#     bucket = client.get_bucket(bucket_name)
#     blob = bucket.blob(destination_blob_name)
#     blob.upload_from_filename(log_file)
#     print(f"Log file uploaded to {bucket_name}/{destination_blob_name}")
