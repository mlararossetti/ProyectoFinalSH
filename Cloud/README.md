# DESARROLLO EN CLOUD

La consolidación de la información comienza con la carga inicial de los datos diarios de viajes correspondientes al periodo de enero de 2021 a julio de 2024 desarrollado en el notebook [ETL_Viajes_Diarios_Agregados_Inicial](/notebooks/1.%20ETL/ELT_Viajes_Diarios_Agregados_Inicial.ipynb). 

Este proceso genera dos archivos agregados de forma mensual: por [industria](/datasets/2.%20Depurados/TLC%20Aggregated%20Data/TLC%20Trip%20Record%20Data_viajes_by_industry.csv) y por zona de pickuop y dropoff (no se sube a GitHub por su tamaño). Estos datasets se almacenan inicialmente en un bucket de Google Cloud Storage. 


## PIPELINE
A través de un proceso de web scraping, implementado mediante una función de Google Cloud Functions programada para ejecutarse mensualmente, se identifican y extraen los nuevos reportes diarios y mensuales disponibles en el sitio web de la TLC.

El proceso llama desde el [main.py](/Cloud/main.py) a la función *get_start_date_from_csv* implementada en [functions.py](/Cloud/functions.py) que detecta la última fecha procesada del archivo [Fechas_Archivos_Levantados.csv](/datasets/2.%20Depurados/Fechas_Archivos_Levantados.csv) que se encuentra en el Bucket de Google.

Luego se corre la función *download_and_upload_to_gcs* para poder:

1. Descargar los archivos parquet de la web de TLC y los disponibiliza en el Bucket.
2. Descarga el archivo [mensual](/datasets/2.%20Depurados/TLC%20Aggregated%20Data/data_reports_monthly.csv) de la web de TLC y lo disponibiliza en el Bucket
3. Escribe en el csv [Fechas_Archivos_Levantados.csv](/datasets/2.%20Depurados/Fechas_Archivos_Levantados.csv) el nuevo mes levantado.

Una vez descargados todos los archivos en el Bucket se corre el proceso de ETL definido en [functions_ETL.py](/Cloud/functions_ETL.py) similar al elaborado para la carga inicial de datos.
En este proceso se crean dos archivos similares a los de la carga inicial pero sólo con el mes levantado: por **industria** y por **zona de pickuop y dropoff**. Estos datasets también se almacenan el bucket de Google Cloud Storage y luego se realiza un merge entre el archivo **mensual**, creando un archivo final llamado [merged_taxi_data](/datasets/2.%20Depurados/TLC%20Aggregated%20Data/merged_taxi_data.csv).

Por último, la función [SQL Big Query](/Cloud/SQL_Big_Query.py), disponibiliza los archivos en Big Query realizando las consultas pertinentes para la carga incremental.