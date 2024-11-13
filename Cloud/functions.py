import logging
import os
import time
import urllib.request
import csv
from io import StringIO
from datetime import datetime
from dateutil.relativedelta import relativedelta
from google.cloud import storage #, pubsub_v1
from gcs_client import GCSClient
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


# Configuración de logging para registrar errores en un archivo log
#log_file = '/tmp/error_log.log'
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

## //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def get_start_date_from_csv(bucket_name, fechas_csv, default_start_date=None):
    """
    Obtiene la fecha de inicio a partir de la última fecha registrada en el archivo CSV en el bucket de GCS.
    Returns:
        datetime: La fecha de inicio calculada o la fecha predeterminada.
    """
    client = GCSClient()
    try:
        data = client.download_blob(bucket_name, fechas_csv)
        last_date_str = data.strip().splitlines()[-1]
        last_date = datetime.strptime(last_date_str, "%d/%m/%Y")
        start_date = last_date + relativedelta(months=1)
    except (IndexError, ValueError) as e:
        logging.error(f"Error al obtener la fecha de inicio de {fechas_csv}: {e}")
        raise ValueError("No se encontró una fecha válida en el archivo CSV y no se especificó una fecha predeterminada.")
    finally:
        client.delete_client()
    return start_date


## //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# Función para verificar y descargar archivos .parquet y subirlos a GCS directamente
def download_and_upload_to_gcs(base_urls, start_date, monthly_url, fechas_csv, bucket_name, retries=3, delay=5):
    
    logging.info("Iniciando la descarga y subida de archivos .parquet y .csv.")
    year_month = start_date.strftime("%Y-%m")
    all_files_downloaded = True # Bandera en caso de que falle la descarga

    for dataset_type, base_url in base_urls.items():
        url = base_url.format(year_month)
        file_name = f"{dataset_type}_tripdata_{year_month}.parquet"
        blob_name = f"TLC Trip Record Data/{file_name}"

        if not download_and_upload_file(url, bucket_name, blob_name, retries, delay):
            all_files_downloaded = False
            break

    if all_files_downloaded:
        csv_blob_name = f"TLC Aggregated Data/tripdata_{year_month}.csv"
        download_and_upload_file(monthly_url, bucket_name, csv_blob_name, retries, delay)
        save_date_to_csv(start_date, bucket_name, fechas_csv)
        logging.info("Todos los archivos .parquet y .csv fueron subidos correctamente.")
    

## //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

# Función para descargar y subir un archivo directamente a Google Cloud Storage
def download_and_upload_file(url, bucket_name, blob_name, retries, delay):
    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(url) as response:
                file_data = response.read()
            client = GCSClient()
            try:
                client.upload_blob_from_parquet(bucket_name, blob_name, file_data)
            finally:
                client.delete_client()
            logging.info(f"Archivo {url} subido a {bucket_name}/{blob_name}.")
            return True
        except Exception as e:
            if attempt == retries:
                logging.error(f"Error al descargar/subir {url}: {e}")
            else:
                logging.warning(f"Reintentando descarga/subida de {url} (Intento {attempt}/{retries})...")
                time.sleep(delay)
    return False


def save_date_to_csv(date, bucket_name, file_path):
    client = GCSClient()
    try:
        rows = client.download_blob(bucket_name, file_path).splitlines() if client.client.bucket(bucket_name).blob(file_path).exists() else []
        output = StringIO()
        writer = csv.writer(output)

        for row in csv.reader(rows):
            writer.writerow(row)
        writer.writerow([date.strftime("%d/%m/%Y")])

        client.upload_blob_from_string(bucket_name, file_path, output.getvalue(), content_type="text/csv")
        logging.info(f"Fecha {date.strftime('%d/%m/%Y')} guardada exitosamente en {file_path}.")
    finally:
        client.delete_client()


# ## //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# ## Se comenta para no generar inconvenientes con github
# def enviar_correo(start_date):
#     """Envía un correo de notificación indicando que los datos se cargaron correctamente."""
    
#     # Define el mensaje y asunto
#     mensaje = f"Los datos de {start_date} fueron cargados y actualizados correctamente en BigQuery."
#     asunto = f"Actualización de datos: {start_date}"

#     # Configura el contenido del correo
#     message = Mail(
#         from_email="marialararossetti@gmail.com",  # Cambia esto a tu correo de remitente
#         to_emails="hernanlussiatti@gmail.com",
#         subject=asunto,
#         plain_text_content=mensaje
#     )

#     try:
#         # Cargar la API key desde la variable de entorno
#         sendgrid_api_key = ''  #os.getenv("SENDGRID_API_KEY")
#         sg = SendGridAPIClient(sendgrid_api_key)
#         print("dsp de instanciar")
#         response = sg.send(message)
#         print("dsp de response")
#         logging.info(f"Correo enviado: {response.status_code}")
#     except Exception as e:
#         logging.error(f"Error al enviar el correo: {e}")
#         raise