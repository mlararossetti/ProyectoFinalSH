# DESARROLLO EN CLOUD

La consolidación de la información comienza con la carga inicial de los datos diarios de viajes correspondientes al periodo de enero de 2021 a julio de 2024 desarrollado en el notebook [ETL_Viajes_Diarios_Agregados_Inicial](/notebooks/1.%20ETL/ELT_Viajes_Diarios_Agregados_Inicial.ipynb). 

Este proceso genera dos archivos agregados de forma mensual: por [industria](/datasets/2.%20Depurados/TLC%20Aggregated%20Data/TLC%20Trip%20Record%20Data_viajes_by_industry.csv) y por zona de pickuop y dropoff (no se sube a GitHub por su tamaño). Estos datasets se almacenan inicialmente en un bucket de Google Cloud Storage. 


## PIPELINE
A través de un proceso de web scraping, implementado mediante una función de Google Cloud Functions programada para ejecutarse mensualmente, se identifican y extraen los nuevos reportes diarios y mensuales disponibles en el sitio web de la TLC.

El proceso llama desde el [main.py](/Cloud/main.py) a la función [get_start_date_from_csv] implementada en [functions.py](/Cloud/functions.py) que detecta la última fecha procesada del archivo [Fechas_Levantadas.csv] que se encuentra en el Bucket de Google.

Luego se corre la función [download_and_upload_to_gcs] para poder:

1. Descargar los archivos parquet de la web de TLC y los disponibiliza en el Bucket.
2. Descarga el archivo mensual de la web de TLC y lo disponibiliza en el Bucket
3. Escribe en el csv [Fechas_Levantadas.csv] el mes nuevo levantado.







Posteriormente, los datos recopilados son procesados y transformados para integrarse de manera eficiente a las tablas existentes en los buckets de almacenamiento.
Finalmente, los datasets procesados se ponen a disposición en formato de tablas utilizando la herramienta BigQuery, facilitando así su consulta y análisis. De esta manera, pueden ser consumidos por PowerBI para generar dashboards interactivos con datos actualizados.