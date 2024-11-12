from google.cloud import storage
from google.auth.exceptions import DefaultCredentialsError
import os
import warnings
warnings.filterwarnings("ignore")


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

    def upload_blob_from_parquet(self, bucket_name, blob_name, file_data):
        """Sube contenido a un blob de GCS desde bytes de archivo."""
        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.upload_from_string(file_data)

    
    def upload_file_to_gcs(self, bucket_name, blob_name, temp_file_path):
        # Subir el archivo CSV al bucket de GCS1
        self.client.upload_blob_from_filename(bucket_name, blob_name, temp_file_path)
        print(f"Archivo CSV '{blob_name}' subido exitosamente a '{bucket_name}'.")


    def delete_client(self):
        """Elimina el cliente de Google Cloud Storage."""
        del self.client

    def download_blob_file (self, bucket_name, blob_name, local_path):
        """Descarga el contenido de un blob de GCS a una ruta local."""
        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        try:
            blob.download_to_filename(local_path)
            print(f"Archivo {blob_name} descargado exitosamente en {local_path}.")
        except Exception as e:
            print(f"Error al descargar el archivo {blob_name}: {e}")
            raise