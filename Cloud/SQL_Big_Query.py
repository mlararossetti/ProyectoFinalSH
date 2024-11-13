from google.cloud import bigquery, storage
from google.api_core.exceptions import NotFound
import os
import warnings
warnings.filterwarnings("ignore")

# Configuración de constantes
PROJECT_ID = 'proyectofinalsh'
DATASET_ID = 'henry_taxis_g5'

if 'GOOGLE_CLOUD_PROJECT' not in os.environ:
        os.environ['GOOGLE_CLOUD_PROJECT'] = 'proyectofinalsh'

# Inicializa los clientes
bigquery_client = bigquery.Client(project=PROJECT_ID)
storage_client = storage.Client(project=PROJECT_ID)

def update_table_from_csv(bucket_name, table_id, csv_file_name):
    
    """Busca el archivo CSV en el bucket y lo carga en la tabla de BigQuery existente."""
    
    # Verifica si el archivo existe en el bucket
    try:
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(csv_file_name)
        
        if not blob.exists():
            raise  Exception(f"Archivo {csv_file_name} no encontrado en el bucket {bucket_name}.")

        uri = f'gs://{bucket_name}/{csv_file_name}'  # Ruta del archivo en GCS
        table_ref = bigquery_client.dataset(DATASET_ID).table(table_id)
        
        # Configura el trabajo de carga
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.CSV,
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE, 
            skip_leading_rows=1,  # Saltar el encabezado del CSV
            autodetect=True  # Detectar el esquema automáticamente
        )

        # Cargar el archivo a BigQuery
        load_job = bigquery_client.load_table_from_uri(
            uri,
            table_ref,
            job_config=job_config
        )

        load_job.result()  # Espera a que el trabajo termine
        
        print(f"Datos nuevos cargados a {DATASET_ID}.{table_id} en BigQuery desde {uri}.")
        
    except Exception as e:
        raise e