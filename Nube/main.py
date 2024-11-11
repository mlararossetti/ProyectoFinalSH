import logging
from google.cloud import storage
from functions import get_start_date_from_csv, download_and_upload_to_gcs # upload_logs_to_gcs.
from io import BytesIO
import warnings
import os

warnings.filterwarnings("ignore")

# Configuración de logging para registrar errores en un archivo log
#log_file = '/tmp/error_log.log'
#logging.basicConfig(filename=log_file, level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuración de ruta y URLs base
base_urls = {
    "yellow": "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{}.parquet",
    "green": "https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_{}.parquet",
    "fhv": "https://d37ci6vzurychx.cloudfront.net/trip-data/fhv_tripdata_{}.parquet",
    "fhvhv": "https://d37ci6vzurychx.cloudfront.net/trip-data/fhvhv_tripdata_{}.parquet",
}
monthly_url = "https://www.nyc.gov/assets/tlc/downloads/csv/data_reports_monthly.csv"

# Nombre del bucket en GCS
bucket_name = 'henry-taxis'

try:
    # Definir las rutas necesarias
    fechas_csv = "Fechas_Archivos_Levantados.csv"
    start_date = get_start_date_from_csv(bucket_name, fechas_csv)
    download_and_upload_to_gcs(base_urls, start_date, monthly_url, fechas_csv, bucket_name)

    print("Terminó OK")

    # Subir los logs a GCS
    #upload_logs_to_gcs(log_file, BUCKET_NAME, "error_log.log")

    # Limpiar el archivo de log temporal
    #os.remove(log_file)
except ValueError as e:
    print(e)
except Exception as e:
    logging.error(f"Error en la ejecución: {e}")
    print(f"Error en la ejecución: {str(e)}")  # Opcional: imprime el error en la consola para más visibilidad
