from google.cloud import storage
from google.auth.exceptions import DefaultCredentialsError
import os
import warnings
import logging
warnings.filterwarnings("ignore")

# Configuración de logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class GCSClient:
    def __init__(self):
        try:
            if 'GOOGLE_CLOUD_PROJECT' not in os.environ:
                os.environ['GOOGLE_CLOUD_PROJECT'] = 'proyectofinalsh'
            # Intentar crear un cliente de GCS
            self.client = storage.Client()
        except DefaultCredentialsError as e:
            # Capturar error de credenciales
            raise ValueError("No se ha podido autenticar. Asegúrate de tener un proyecto configurado o las credenciales de una cuenta de servicio.") from e

    def download_blob(self, bucket_name, blob_name):
        """Descarga el contenido de un blob de GCS."""
        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        return blob.download_as_text()


    def upload_blob_from_string(self, bucket_name, blob_name, content, content_type="text/plain"):
        """Sube contenido a un blob de GCS desde una cadena."""
        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.upload_from_string(content, content_type=content_type)
        logging.info(f"Archivo subido exitosamente a {bucket_name}/{blob_name}.")

  
    def upload_blob_from_parquet(self, bucket_name, blob_name, file_data):
        """Sube contenido a un blob de GCS desde bytes de archivo."""
        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.upload_from_string(file_data)
        logging.info(f"Archivo subido exitosamente a {bucket_name}/{blob_name}.")

    
    def upload_file_to_gcs(self, bucket_name, blob_name, temp_file_path):
         # Obtener el bucket
        bucket = self.client.bucket(bucket_name)
        # Crear un blob en el bucket con el nombre especificado
        blob = bucket.blob(blob_name)
        # Subir el archivo
        blob.upload_from_filename(temp_file_path)
        logging.info(f"Archivo CSV '{blob_name}' subido exitosamente a '{bucket_name}'.")


    def delete_client(self):
        """Elimina el cliente de Google Cloud Storage."""
        del self.client


    def download_blob_file (self, bucket_name, blob_name, local_path):
        """Descarga el contenido de un blob de GCS a una ruta local."""
        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        try:
            blob.download_to_filename(local_path)
            logging.info(f"Archivo {blob_name} descargado exitosamente en {local_path}.")
        except Exception as e:
            logging.error(f"Error al descargar el archivo {blob_name}: {e}")
            raise