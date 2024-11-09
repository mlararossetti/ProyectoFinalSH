import logging
from google.cloud import storage
from functions import get_start_date_from_csv, download_and_upload_to_gcs, upload_logs_to_gcs
from functions_ETL import ETL_Viajes_Diarios

from io import BytesIO


import warnings 
warnings.filterwarnings("ignore")



# Configuración del Bucket (usando GCS)
output_folder = 'gs://henry-taxis'  # Ruta del Bucket en GCS

# Configuración de logging para registrar errores en un archivo log
# Primero, guardaremos los logs localmente y luego los subimos a GCS

# Configuración de ruta y URLs base
base_urls = {
    "yellow": "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{}.parquet",
    "green": "https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_{}.parquet",
    "fhv": "https://d37ci6vzurychx.cloudfront.net/trip-data/fhv_tripdata_{}.parquet",
    "fhvhv": "https://d37ci6vzurychx.cloudfront.net/trip-data/fhvhv_tripdata_{}.parquet",
}

csv_url = "https://www.nyc.gov/assets/tlc/downloads/csv/data_reports_monthly.csv"
csv_file_path = output_folder + "/data_reports_monthly.csv"  # Ruta de archivo CSV




# Nombre del bucket en GCS
BUCKET_NAME = 'henry-taxis'

# Definir las rutas necesarias
fechas_csv = output_folder + "/Fechas_Archivos_Levantados.csv"
start_date = get_start_date_from_csv(fechas_csv)
download_and_upload_to_gcs(base_urls, output_folder, start_date, csv_url, fechas_csv, BUCKET_NAME) 

print("Terminó OK")

#     # Subir los logs a GCS
#     upload_logs_to_gcs(log_file, "henry-taxis", "error_log.log")

#     # Limpiar el archivo de log temporal
#     os.remove(log_file)
    

# except Exception as e:
#     logging.error(f"Error en la ejecución: {e}")
#     return f"Error: {str(e)}", 500








# # Subir el archivo de log a GCS después de la ejecución
# upload_logs_to_gcs(log_file, "henry-taxis", "error_log.log")

# # Limpiar el archivo temporal
# os.remove(log_file)


