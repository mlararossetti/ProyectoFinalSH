import logging
import warnings
from google.cloud import pubsub_v1
from functions import get_start_date_from_csv, download_and_upload_to_gcs, enviar_correo
from functions_ETL import process_taxi_data
from SQL_Big_Query import update_table_from_csv
import functions_framework


warnings.filterwarnings("ignore")


# Configuración de logging para registrar errores en un log
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


@functions_framework.http
def load_data_function(request):
    # Configura el proyecto y el tema de Pub/Sub
    project_id = "proyectofinalsh"
    topic_id = "file_download_complete"
    message_text = "Archivos cargados correctamente"
    # Bucket y archivos
    bucket_name = "henry-taxis-g5"
    fechas_csv = "Fechas_Archivos_Levantados.csv"


    # URLs base para descargar datos
    base_urls = {
        "yellow": "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{}.parquet",
        "green": "https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_{}.parquet",
        "fhv": "https://d37ci6vzurychx.cloudfront.net/trip-data/fhv_tripdata_{}.parquet",
        "fhvhv": "https://d37ci6vzurychx.cloudfront.net/trip-data/fhvhv_tripdata_{}.parquet",
    }
    monthly_url = "https://www.nyc.gov/assets/tlc/downloads/csv/data_reports_monthly.csv"


    try:
        # Obtiene última fecha cargada
        start_date = get_start_date_from_csv(bucket_name, fechas_csv)
        # Descarga los archivos en el bucket
        download_and_upload_to_gcs(base_urls, start_date, monthly_url, fechas_csv, bucket_name)
        # Realiza el proceso de ETL y carga incremental
        process_taxi_data (bucket_name, start_date)
        
        # Carga los datos en Big Query
        TABLE_ID = 'Data_viajes_by_industry'
        CSV_FILE_NAME = 'TLC Aggregated Data/TLC Trip Record Data_viajes_by_industry.csv'  
            
        update_table_from_csv(bucket_name,TABLE_ID,CSV_FILE_NAME)
        
        TABLE_ID = 'Data_viajes_by_location'
        CSV_FILE_NAME = 'TLC Aggregated Data/TLC Trip Record Data_viajes_by_location.csv'
        update_table_from_csv(bucket_name,TABLE_ID,CSV_FILE_NAME)
        
        # Envía un correo para avisar que finalizó
        enviar_correo(start_date)    

        # publish_message(project_id, topic_id, message_text, start_date)
        print("Proceso completado correctamente y mensaje enviado.")
    except ValueError as e:
        logging.error(f"Error de valor: {e}")
    except Exception as e:
        logging.error(f"Error en la ejecución: {str(e)}")