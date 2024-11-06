# EDA de Datasets

## Datasets de Viajes

Los datos se obtienen de la web de la [Comisión de Taxis y Limusinas (TLC)](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page).

Hay 4 tipos de licenciamientos de vehículos:
   - `Taxis Amarillos`: Son los taxis más reconocibles de Nueva York y están autorizados para recoger pasajeros en la calle. Estos vehículos tienen un medallón que indica su licencia.

   - `Taxis Verdes (Boro Taxis)`: Introducidos para atender áreas de la ciudad que no son servidas por taxis amarillos, estos pueden recoger pasajeros en áreas de los cinco boroughs, excepto Manhattan.

   - `For-Hire Vehicles (FHVs)`: Los vehículos de alquiler (For-Hire Vehicles, FHVs) son una parte integral del sistema de transporte de Nueva York. Son vehículos que están afiliados a bases de vehículos de alquiler y que ofrecen servicios de transporte a través de despachos preorganizados en toda la ciudad de Nueva York. Estos vehículos no pueden ser detenidos en la calle como los taxis amarillos, y su uso generalmente implica la reserva previa a través de aplicaciones o servicios telefónicos.

   - `FHV - High Volume (FHVHV)`:Los FHVs de alto volumen son aquellos vehículos que están afiliados a bases de alquiler que despachan al menos 10.000 viajes por día. Actualmente, Lyft y Uber son las únicas bases que están autorizadas y clasificadas como FHV - High Volume.


### Tareas realizadas
- Se confeccionó un ETL que Screapea los datasets disponibles.
- Para la elaboración del EDA se utilizó el set de datos del Enero 2021.
- Se cargaron los datasets en 4 DataFrames y se eliminaron duplicados de cada uno de forma indificidual.
    - Sólo presentaron duplicados los datasets de FHV y FHVHV.
- Se trabajó sobre los datos para unificar la información en un único dataframe. Para ello se analizaron los diccionarios de datos y se elaboró una tabla de campos en común:


| Nombre unificadoInc      | Yellow Taxis            | Green Taxis             | High Volume FHV        | FHV - Other           | Dato                                                                                      |
|-----------------------|-------------------------|-------------------------|------------------------|-----------------------|------------------------------------------------------------------------------------------|
| pickup_datetime       | tpep_pickup_datetime    | lpep_pickup_datetime    | pickup_datetime        | pickup_datetime       | The date and time when the meter was engaged / The date and time of the trip pick-up     |
| dropoff_datetime      | tpep_dropoff_datetime   | lpep_dropoff_datetime   | dropoff_datetime       | dropoff_datetime      | The date and time when the meter was disengaged / The date and time of the trip drop-off |
| pickup_location_id    | PULocationID            | PULocationID            | PULocationID           | PUlocationID          | TLC Taxi Zone in which the taximeter was engaged / TLC Taxi Zone in which the trip began |
| dropoff_location_id   | DOLocationID            | DOLocationID            | DOLocationID           | DOlocationID          | TLC Taxi Zone in which the taximeter was disengaged / TLC Taxi Zone in which the trip ended|
| passenger_count       | passenger_count         | passenger_count         | No hay dato            | No hay dato           | The number of passengers in the vehicle.                                                 |
| trip_distance         | trip_distance           | trip_distance           | trip_miles             | No hay dato           | The elapsed trip distance in miles reported by the taximeter. / total miles for passenger trip |
| payment_type          | payment_type            | payment_type            | No hay dato            | No hay dato           | A numeric code signifying how the passenger paid for the trip.                           |
| fare_amount           | fare_amount             | fare_amount             | base_passenger_fare    | No hay dato           | The time-and-distance fare calculated by the meter/ Base passenger fare before tolls, tips, taxes, and fees |
| total_amount          | total_amount            | total_amount            | total_amount (Creado)  | No hay dato           | The total amount charged to passengers. Does not include cash tips. / Campo Creado a partir de: base_passenger_fare - sales_tax - bcf - tips - tolls |
| congestion_surcharge  | congestion_surcharge    | congestion_surcharge    | congestion_surcharge   | No hay dato           | Total amount collected in trip for NYS congestion surcharge.                             |
| shared_request_flag   | No hay dato             | No hay dato             | shared_request_flag    | No hay dato           | Did the passenger agree to a shared/pooled ride, regardless of whether they were matched? (Y/N) |
| shared_match_flag     | No hay dato             | No hay dato             | shared_match_flag      | SR_Flag               | Did the passenger share the vehicle with another passenger who booked separately at any point during the trip? (Y/N) |
|                       | VendorID                | VendorID                | hvfhs_license_num      | dispatching_base_num  | Otros datos no utilizados. Tomar de referencia los diccionarios de datos originales.    |
|                       | store_and_fwd_flag      | dispatching_base_num    | SR_Flag                |                       | Otros datos no utilizados. Tomar de referencia los diccionarios de datos originales.    |
|                       | RatecodeID              | originating_base_num    | Affiliated_base_number |                       | Otros datos no utilizados. Tomar de referencia los diccionarios de datos originales.    |
|                       | extra                   | request_datetime        |                        |                       | Otros datos no utilizados. Tomar de referencia los diccionarios de datos originales.    |
|                       | mta_tax                 | on_scene_datetime       |                        |                       | Otros datos no utilizados. Tomar de referencia los diccionarios de datos originales.    |
|                       | tip_amount              | tolls                   |                        |                       | Otros datos no utilizados. Tomar de referencia los diccionarios de datos originales.    |
|                       | tolls_amount            | bcf                     |                        |                       | Otros datos no utilizados. Tomar de referencia los diccionarios de datos originales.    |
|                       | ehail_fee               | sales_tax               |                        |                       | Otros datos no utilizados. Tomar de referencia los diccionarios de datos originales.    |
|                       | improvement_surcharge   | trip_time               |                        |                       | Otros datos no utilizados. Tomar de referencia los diccionarios de datos originales.    |
|                       | congestion_surcharge    | airport_fee             |                        |                       | Otros datos no utilizados. Tomar de referencia los diccionarios de datos originales.    |
|                       | trip_type               | congestion_surcharge    |                        |                       | Otros datos no utilizados. Tomar de referencia los diccionarios de datos originales.    |
|                       |                         | tips                    |                        |                       | Otros datos no utilizados. Tomar de referencia los diccionarios de datos originales.    |
|                       |                         | driver_pay              |                        |                       | Otros datos no utilizados. Tomar de referencia los diccionarios de datos originales.    |
|                       |                         | shared_request_flag     |                        |                       | Otros datos no utilizados. Tomar de referencia los diccionarios de datos originales.    |
|                       |                         | shared_match_flag       |                        |                       | Otros datos no utilizados. Tomar de referencia los diccionarios de datos originales.    |
|                       |                         | access_a_ride_flag      |                        |                       | Otros datos no utilizados. Tomar de referencia los diccionarios de datos originales.    |
|                       |                         | wav_request_flag        |                        |                       | Otros datos no utilizados. Tomar de referencia los diccionarios de datos originales.    |
|                       |                         | wav_match_flag          |                        |                       | Otros datos no utilizados. Tomar de referencia los diccionarios de datos originales.    |


- Se reemplazaron los valores de Y y N por valores booleanos True y False.
- Se creó un campo "industry" para determinar bajo que tipo de licenciamiento se realiza cada viaje.
- Se unificaron en un único dataset todos los datos.
- Se adaptaron los tipos de datos de las columnas correspondientes.
- Se elaboró un reporte con [ProfileReport](../../ProfileReports/ProfileReport_1.html).
    - No falta ninguna fecha pero, **`pickup_datetime`** y **`dropoff_datetime`**: 
        - Se corrigieron fechas y se eliminaron registros con fechas de períodos que no corresponden al dataset.
    - Se investigan valores nulos de **`pickup_location_id`** y **`dropoff__location_id`**.
        - Todos los nulos son de la categoría de Industria FHV - Other la cual tiene la peor calidad de información.
        - Dejamos el set de datos ya que cuenta para la cantidad de viajes total.
        - Se reemplazó con nulo los valores 0 de cantidad de pasajeros.

- Se detectaron y corrieron outliers. Se completaron datos faltantes:
    - Distancia de Viajes: 
        - Eliminación de outliers por método de Rango Intercuartílico ya que es los valores extremos son muy elevados y alejados de la media con mínimo en 0.01. Se reemplazan los valores por nulos pero no se eliminan del dataset ya que cuentan para la cantidad de viajes.
        - Se completan los datos faltantes con los valores de distancia promedio entre pickup_locations_id y dropoff_locations_id
    - Tarifa Base: 
        - Eliminación de outliers por método de Rango Intercuartílico ya que es los valores extremos son muy elevados y alejados de la media con mínimo en 0.01. Se reemplazan los valores por nulos pero no se eliminan del dataset ya que cuentan para la cantidad de viajes.
    - Tarifa Total:
        - Valores negativos se pasan a nulos.
        - Se observa que podrían haber algunos outliers, se decide correlacionar con Tarifa Base para determinar si esto es así.
        - No puede haber valor de Tarifa Total si Tarifa Base es nulo.
        - Se elabora una correlación contra Tarifa Base. Los valores de Tarifa Total muy alejados, podrían estar relacionados con Propinas elevadas.
        - Si luego se debe realizar una estimación de Tarifa Total, no es útil tener valores que tengan una relación tan alejada con Tarifa Base, por lo que se excluirán valores.
        - Se decide considerar el percentil 99.99% de los residuos de la correlación lineal. Si se utiliza el 99% se elimina mucha información que no parece ser outlier.
    - Tarifa de congestión:
        - Valores negativos se pasan a nulos.
    - Shared Match Flag:
        - Se modifica el valor del flag **`shared_match_flag`** para contemplar los casos en que el viaje tuvo más de un pasajero.
    - Duración de los viajes:
        - Hay valores negativos de tiempo. Son todos en el dataset de Taxis Amarillos. Se invierten los valores de **`pickup_datatime`** y **`dropoff_datatime`** en este caso.
        - Hay algunos valores extremos muy elevados. Para los outliers (percentil 99.9%) se modifica **`dropoff_datetime`** en función del valor medio de duración del viaje para la relación entre **`pickup_location_id`** y **`dropoff_location_id`**.

    
### Conclusiones    
- La mayoría de los viajes son con un único pasajero
- 82% de los viajes se realizan bajo el licenciamiento del tipo FHV - High Volume (empresas como Uber)
- Se observa que sólo el 2% de los viajes son compartidos.
- Esto podría tener gran implicancia en la reducción de la huella de carbono.
- Las correlaciones más elevadas se dan para:
    - trip_distance con fare_amount y total_amount
    - trip_duration con fare_amount y total_amount