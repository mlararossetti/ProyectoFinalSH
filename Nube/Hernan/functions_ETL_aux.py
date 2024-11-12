from datetime import datetime
import pandas as pd
import numpy as np
from google.cloud import storage
import gc
from sklearn.linear_model import LinearRegression # type: ignore
from pandas.tseries.offsets import MonthEnd
from gcs_client import GCSClient

def process_taxi_data (bucket_name, start_date):


    #start_date = datetime.strptime(start_date, "%Y-%m-%d")
    year_month = start_date.strftime("%Y-%m")  # Extrae el año y mes en formato YYYY-MM


#///////////////////////////////////////////////////////////////////////////////////////
    # Cliente de Cloud Storage
    client = GCSClient()

#///////////////////////////////////////////////////////////////////////    
    # Agregación industry
    try:
        # Intentar descargar el archivo existente
        client = GCSClient()
        blob_name = "TLC Aggregated Data/TLC Trip Record Data_viajes_by_industry.csv"
        temp_local = "/tmp/TLC Trip Record Data_viajes_by_industry.csv"    
        client.download_blob_file(bucket_name, blob_name, temp_local)
       
        # Cargar el archivo existente en un DataFrame
        df_by_industry_old = pd.read_csv(temp_local)
        df_by_industry_old['date'] = pd.to_datetime(df_by_industry_old['date'], format='%Y-%m-%d')
        
    except Exception as e:
        # Si el archivo no existe, crear un DataFrame vacío con las columnas necesarias
        print(f"Archivo no encontrado en {blob_name}. Se creará uno nuevo.")

    # Concatenar el DataFrame existente con el nuevo DataFrame
    df_by_industry_new = df_by_industry_old

    # Guardar el DataFrame actualizado en un archivo temporal local
    #df_by_industry_new.to_csv(temp_local, index=False)

    # Subir el archivo actualizado al bucket en Cloud Storage
    #client.upload_file_to_gcs(bucket_name, blob_name, temp_local)
    #print(f"Archivo actualizado guardado en {blob_name} en Cloud Storage.")

    # Eliminar el cliente GCS después de usarlo
    client.delete_client()

    # Liberar memoria
    del df_by_industry_old
    gc.collect()

#///////////////////////////////////////////////////////////////////////
    print("Carga datos mensuales")

    # Agregación al archivo Mensual
    try:
        # Intentar descargar el archivo existente
        client = GCSClient()
        blob_name = f"TLC Aggregated Data/tripdata_{year_month}.csv"
        temp_local = f"/tmp/tripdata_{year_month}.csv"    
        client.download_blob_file(bucket_name, blob_name, temp_local)
       
        # Cargar el archivo existente en un DataFrame
        df = pd.read_csv(temp_local)
        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
        
    except Exception as e:
        # Si el archivo no existe, crear un DataFrame vacío con las columnas necesarias
        print(f"Archivo no encontrado en {blob_name}. Se creará uno nuevo.")


# #///////////////////////////////////////////////////////////////////////
    # ETL de datos mensuales

    df.columns = [
    'date', 'industry', 'trips_per_day', 'farebox_per_day',
    'unique_drivers', 'unique_vehicles', 'vehicles_per_day',
    'avg_days_vehicles_on_road', 'avg_hours_per_day_per_vehicle',
    'avg_days_drivers_on_road', 'avg_hours_per_day_per_driver',
    'avg_minutes_per_trip', 'percent_of_trips_paid_with_credit_card',
    'trips_per_day_shared'
]

    # Columnas incuidas
    columns_to_replace = df.columns.difference(['date', 'industry'])
    # Reemplazar '-' por '' en las columnas seleccionadas
    df[columns_to_replace] = df[columns_to_replace].replace({'-':np.nan,',':'','%': ''}, regex=True)

    df['date'] = pd.to_datetime(df['date'], format='%Y-%m')
    df['industry'] = df['industry'].astype('category')
    df['trips_per_day'] = df['trips_per_day'].astype('Int64')
    df['farebox_per_day'] = df['farebox_per_day'].astype('Int64')
    df['unique_drivers'] = df['unique_drivers'].astype('Int64')
    df['unique_vehicles'] = df['unique_vehicles'].astype('Int64')
    df['vehicles_per_day'] = df['vehicles_per_day'].astype('Int64')
    df['percent_of_trips_paid_with_credit_card'] = pd.to_numeric(df['percent_of_trips_paid_with_credit_card'], errors='coerce') / 100
    df['trips_per_day_shared'] = pd.to_numeric(df['trips_per_day_shared'], errors='coerce') 

    # Reemplazar 'Green' y 'Yellow' para igual al datset diario
    df['industry'] = df['industry'].replace({'Green': 'Green Taxi', 'Yellow': 'Yellow Taxi'})

    # Agregar "FHV - Other" a las categorías de la columna 'industry' para reemplazar las que no están en el datset diario  
    df['industry'] = df['industry'].cat.add_categories('FHV - Other')

    # Luego, realizar la asignación de las industrias
    other_industries = ['FHV - Black Car', 'FHV - Livery', 'FHV - Lux Limo']
    df.loc[df['industry'].isin(other_industries), 'industry'] = 'FHV - Other'

    # Agrupar por 'month_year' y 'industry', y agregar 'FHV - Other' por mes
    df_other = df[df['industry'] == 'FHV - Other'].groupby('date').agg({
        'trips_per_day': 'sum',
        'farebox_per_day': 'sum',
        'unique_drivers': 'sum',
        'unique_vehicles': 'sum',
        'vehicles_per_day': 'sum',
        'avg_days_vehicles_on_road': 'mean',
        'avg_hours_per_day_per_vehicle': 'mean',
        'avg_days_drivers_on_road': 'mean',
        'avg_hours_per_day_per_driver': 'mean',
        'avg_minutes_per_trip': 'mean',
        'percent_of_trips_paid_with_credit_card': 'mean',
        'trips_per_day_shared': 'sum'
    }).reset_index()

    # Reasignar índices y juntar los DataFrames
    df_other['industry'] = 'FHV - Other'  # Asegurarse de que la columna 'industry' sea consistente
    df = pd.concat([df[df['industry'] != 'FHV - Other'], df_other], ignore_index=True)

    # Acululamos desde el 2021
    df = df[df['date'] >= '2021-01-01']

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    # Aseguro el tipo de date
    df_by_industry_new['date'] = pd.to_datetime(df_by_industry_new['date'], errors='coerce')
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df_total = pd.merge(df,df_by_industry_new, on=['date', 'industry'], how='outer')

   # Liberar memoria
    del df_by_industry_new, df
    gc.collect()

    print("merge de datos mensuakes")
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

     # Obtener la cantidad de días en el mes de cada registro
    df_total['days_in_month'] = df_total['date'].dt.days_in_month
    # Calcular total_trips como trips_per_day * days_in_month
    df_total['total_trips'] = df_total['trips_per_day'] * df_total['days_in_month']

    # Crear el nuevo campo 'farebox_per_day' con valores diferenciados
    df_total['farebox_per_day'] = np.where(
        df_total['industry'] == 'FHV - High Volume',
        df_total['total_amount'] / df_total['days_in_month'],
        df_total['farebox_per_day']
    )

    # Crear el nuevo campo 'total_amount' con valores diferenciados
    df_total['total_amount'] = np.where(
        df_total['industry'] == 'FHV - High Volume',
        df_total['total_amount'],
        df_total['farebox_per_day'] * df_total['days_in_month']
    )

    # Lo mismo pero para cantidad de viajes compartidos
    df_total['shared_match_flag'] = np.where(
        df_total['industry'] == 'FHV - High Volume',
        df_total['trips_per_day_shared'] * df_total['days_in_month'],
        df_total['shared_match_flag']
    )

    # Lo mismo pero para cantidad de viajes compartidos
    df_total['trips_per_day_shared'] = np.where(
        df_total['industry'] == 'FHV - High Volume',
        df_total['trips_per_day_shared'],
        df_total['shared_match_flag'] / df_total['days_in_month']
    )

    df_total['farebox_per_day_per_distance']=df_total['farebox_per_day']/df_total['avg_trip_distance']

    df_total['total_co2_emission'] = df_total['avg_trip_distance'] * df_total['total_trips'] * 400 / 1000000


    # Redondear las columnas de tipo DECIMAL antes de cargarlas en SQL
    df_total['farebox_per_day'] = df_total['farebox_per_day'].round(2)
    df_total['avg_days_vehicles_on_road'] = df_total['avg_days_vehicles_on_road'].round(2)
    df_total['avg_hours_per_day_per_vehicle'] = df_total['avg_hours_per_day_per_vehicle'].round(2)
    df_total['avg_days_drivers_on_road'] = df_total['avg_days_drivers_on_road'].round(2)
    df_total['avg_hours_per_day_per_driver'] = df_total['avg_hours_per_day_per_driver'].round(2)
    df_total['percent_of_trips_paid_with_credit_card'] = df_total['percent_of_trips_paid_with_credit_card'].round(2)
    df_total['avg_trip_distance'] = df_total['avg_trip_distance'].round(2)
    df_total['avg_trip_duration'] = df_total['avg_trip_duration'].round(2)
    df_total['total_amount'] = df_total['total_amount'].round(2)
    df_total['farebox_per_day_per_distance'] = df_total['farebox_per_day_per_distance'].round(4)
    df_total['total_co2_emission'] = df_total['total_co2_emission'].round(4)

    # Empezamos a trabajar con el dataset eliminando columnas o componiendo datos
    df_total = df_total.drop(columns=['year', 'month','trip_distance','trip_duration','fare_amount','avg_minutes_per_trip'])
    df_total['farebox_per_day'] = df_total['farebox_per_day'].replace(0, np.nan) 
    df_total['trips_per_day_shared'] = df_total['trips_per_day_shared'].replace(0, np.nan) 
    df_total['passenger_count'] = df_total['passenger_count'].replace(0, np.nan) 
    df_total['total_amount'] = df_total['total_amount'].replace(0, np.nan) 
    df_total['shared_match_flag'] = df_total['shared_match_flag'].replace(0, np.nan)
    df_total['farebox_per_day_per_distance'] = df_total['farebox_per_day_per_distance'].replace(0, np.nan)

    # Eliminar columnas duplicadas
    df_total = df_total.loc[:, ~df_total.columns.duplicated()]

    
    # Guardar el DataFrame actualizado en un archivo temporal local
    temp_local = "/tmp/merged_taxi_data.csv"
    df_total.to_csv(temp_local, index=False)

    # Subir el archivo actualizado al bucket en Cloud Storage
    client = GCSClient()
    blob_name = "TLC Aggregated Data/merged_taxi_data.csv"
    client.upload_file_to_gcs(bucket_name, blob_name, temp_local)
    print(f"Archivo actualizado guardado en {blob_name} en Cloud Storage.")

    # Eliminar el cliente GCS después de usarlo
    client.delete_client()

    # Liberar memoria
    del df_total
    gc.collect()