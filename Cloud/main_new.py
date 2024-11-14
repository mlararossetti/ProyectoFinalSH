import logging
import warnings
from google.cloud import pubsub_v1
from functions import get_start_date_from_csv, download_and_upload_to_gcs, enviar_correo, save_date_to_csv
from functions_ETL import process_taxi_data
from SQL_Big_Query import update_table_from_csv
import functions_framework

warnings.filterwarnings("ignore")


# Configuración de logging para registrar errores en un log
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


@functions_framework.http
def load_data(request):
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
        all_files_downloaded = download_and_upload_to_gcs(base_urls, start_date, monthly_url, fechas_csv, bucket_name)
        
        if all_files_downloaded:
            logging.info("Descarga de archivos completada.")
    except ValueError as e:
        logging.error(f"Error de valor: {e}")
        return f"Error de valor: {e}", 500
    except Exception as e:
        logging.error(f"Error en la ejecución: {str(e)}")
        return f"Error en la ejecución: {str(e)}", 500

    try:
        if all_files_downloaded:
            process_taxi_data(bucket_name, start_date)

            update_table_from_csv(bucket_name, 'Data_viajes_by_industry', 'TLC Aggregated Data/TLC Trip Record Data_viajes_by_industry.csv')
            update_table_from_csv(bucket_name, 'Data_viajes_by_location', 'TLC Aggregated Data/TLC Trip Record Data_viajes_by_location.csv')

            enviar_correo(start_date)
            save_date_to_csv(start_date, bucket_name, fechas_csv)

        logging.info("Proceso completado correctamente y mensaje enviado.")
        return "Proceso completado correctamente y mensaje enviado.", 200
    except ValueError as e:
        logging.error(f"Error de valor: {e}")
        return f"Error de valor: {e}", 500
    except Exception as e:
        logging.error(f"Error en la ejecución: {str(e)}")
        return f"Error en la ejecución: {str(e)}", 500