import logging
from google.cloud import storage
import os
from functions import get_start_date_from_csv, download_file, upload_to_gcs

# Configuración del Bucket (usando GCS)
output_folder = 'gs://henry-taxis'  # Ruta del Bucket en GCS

# Configuración de logging para registrar errores en un archivo log
# Primero, guardaremos los logs localmente y luego los subimos a GCS
log_file = '/tmp/error_log.log'  # Archivo local temporal para logs
logging.basicConfig(filename=log_file, level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuración de ruta y URLs base
base_urls = {
    "yellow": "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{}.parquet",
    "green": "https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_{}.parquet",
    "fhv": "https://d37ci6vzurychx.cloudfront.net/trip-data/fhv_tripdata_{}.parquet",
    "fhvhv": "https://d37ci6vzurychx.cloudfront.net/trip-data/fhvhv_tripdata_{}.parquet",
}

csv_url = "https://www.nyc.gov/assets/tlc/downloads/csv/data_reports_monthly.csv"
csv_file_path = output_folder + "/data_reports_monthly.csv"  # Ruta de archivo CSV



# Función para subir los logs a GCS
def upload_logs_to_gcs(log_file, bucket_name, destination_blob_name):
    """Sube un archivo de log desde el sistema local a un bucket de GCS."""
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(log_file)
    print(f"Log file uploaded to {bucket_name}/{destination_blob_name}")

# Subir el archivo de log a GCS después de la ejecución
upload_logs_to_gcs(log_file, "henry-taxis", "error_log.log")

# Limpiar el archivo temporal
os.remove(log_file)


# La función de Cloud Functions debe aceptar "request"
def process_files(request):
    try:
        # Definir las rutas necesarias
        fechas_csv = "gs://henry-taxis/fechas_levantadas.csv"
        start_date = get_start_date_from_csv(fechas_csv)
        download_file(base_urls, output_folder, start_date, csv_url, fechas_csv)

        # Subir los logs a GCS
        upload_logs_to_gcs(log_file, "henry-taxis", "error_log.log")

        # Limpiar el archivo de log temporal
        os.remove(log_file)

        return "Proceso completado correctamente", 200

    except Exception as e:
        logging.error(f"Error en la ejecución: {e}")
        return f"Error: {str(e)}", 500


