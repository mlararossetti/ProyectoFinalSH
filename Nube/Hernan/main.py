import logging
import colorlog

import warnings
from google.cloud import pubsub_v1
from functions import get_start_date_from_csv, download_and_upload_to_gcs, publish_message
from functions_ETL import process_taxi_data
warnings.filterwarnings("ignore")


# Configura el proyecto y el tema de Pub/Sub
project_id = "proyectofinalsh"
topic_id = "file_download_complete"
message_text = "Archivos cargados correctamente"
# Bucket y archivos
bucket_name = "henry-taxis-g5"
fechas_csv = "Fechas_Archivos_Levantados.csv"


# Configuración de logging para registrar errores en un archivo log
#log_file = '/tmp/error_log.log'
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = colorlog.StreamHandler()
# Definir el formato con colores
formatter = colorlog.ColoredFormatter(
    "%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    reset=True,
    log_colors={
        'DEBUG': 'cyan',     # Azul para Debug
        'INFO': 'green',     # Verde para Info
        'WARNING': 'yellow', # Amarillo para Warning
        'ERROR': 'red',      # Rojo para Error
        'CRITICAL': 'bold_red', # Rojo negrita para Critical
    }
)
# Asignar el formatter al handler
handler.setFormatter(formatter)

# Agregar el handler al logger
logger.addHandler(handler)

# Ejemplos de mensajes
logger.info("Este es un mensaje informativo.")
logger.error("Este es un mensaje de error.")



# Configuración de logging para registrar errores en un archivo log
#log_file = '/tmp/error_log.log'
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# URLs base para descargar datos
base_urls = {
    "yellow": "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{}.parquet",
    "green": "https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_{}.parquet",
    "fhv": "https://d37ci6vzurychx.cloudfront.net/trip-data/fhv_tripdata_{}.parquet",
    "fhvhv": "https://d37ci6vzurychx.cloudfront.net/trip-data/fhvhv_tripdata_{}.parquet",
}
monthly_url = "https://www.nyc.gov/assets/tlc/downloads/csv/data_reports_monthly.csv"


try:
    start_date = get_start_date_from_csv(bucket_name, fechas_csv)
    download_and_upload_to_gcs(base_urls, start_date, monthly_url, fechas_csv, bucket_name)
    process_taxi_data (bucket_name, start_date)
    # publish_message(project_id, topic_id, message_text, start_date)
    print("Proceso completado correctamente y mensaje enviado.")
except ValueError as e:
    logging.error(f"Error de valor: {e}")
except Exception as e:
    logging.error(f"Error en la ejecución: {str(e)}")