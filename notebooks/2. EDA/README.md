# EDA de Datasets

---
## Datasets de Viajes Diarios

Los datos se obtienen de la web de la [Comisión de Taxis y Limusinas (TLC)](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page).

Hay 4 tipos de licenciamientos de vehículos:
   - `Taxis Amarillos`: Son los taxis más reconocibles de Nueva York y están autorizados para recoger pasajeros en la calle. Estos vehículos tienen un medallón que indica su licencia.

   - `Taxis Verdes (Boro Taxis)`: Introducidos para atender áreas de la ciudad que no son servidas por taxis amarillos, estos pueden recoger pasajeros en áreas de los cinco boroughs, excepto Manhattan.

   - `For-Hire Vehicles (FHVs)`: Los vehículos de alquiler (For-Hire Vehicles, FHVs) son una parte integral del sistema de transporte de Nueva York. Son vehículos que están afiliados a bases de vehículos de alquiler y que ofrecen servicios de transporte a través de despachos preorganizados en toda la ciudad de Nueva York. Estos vehículos no pueden ser detenidos en la calle como los taxis amarillos, y su uso generalmente implica la reserva previa a través de aplicaciones o servicios telefónicos.

   - `FHV - High Volume (FHVHV)`: Los FHVs de alto volumen son aquellos vehículos que están afiliados a bases de alquiler que despachan al menos 10.000 viajes por día. Actualmente, Lyft y Uber son las únicas bases que están autorizadas y clasificadas como FHV - High Volume.


### Tareas realizadas
- Se confeccionó un [ETL](../../notebooks/1.%20ETL/Scrapping_Datasets.ipynb) que Screapea los datasets disponibles desde el año 2021 y los descarga localmente.
- Para la elaboración del EDA se utilizó el set de datos del Enero 2021.
- Se analizaron duplicados, nulos y outliers en el notebook [EDA_Viajes_Diarios 1](./EDA_Viajes_Diarios%201.ipynb) y se realizó el análsis de las distintas variables en el [EDA_Viajes_Diarios 2](./EDA_Viajes_Diarios%202.ipynb)
- Se cargaron los datasets en 4 DataFrames y se eliminaron duplicados de cada uno de forma individual.
    - Sólo presentaron duplicados los datasets de FHV y FHVHV.
- Se trabajó sobre los datos para unificar la información en un único dataframe. Para ello se analizaron los diccionarios de datos y se elaboró una tabla de campos en común disponibilizada en el [Diccionario de Datos](../../datasets/1.%20Originales/dictionarys/Diccionario%20de%20Datos.xlsx)


| Nuevo Nombre     | Yellow Taxis            | Green Taxis             | High Volume FHV        | FHV - Other           | Descripción                                                                                      |
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

- Se detectaron y corrigieron outliers. Se completaron datos faltantes:
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
- Se incoporó el archivo Shape de [Zonas de Nueva York](../../datasets/1.%20Originales/taxi_zones/taxi_zones.shp) para el análisis geográfico.
- Se incoporó el datset de [Feriados de Nueva York](../../datasets/1.%20Originales/feriados_nacionales_2021_2024.csv) para el análsisi de días Laborables y no Laborables.

    
### Conclusiones    
- Buena calidad de datos de los datasets **`Yellow Taxis`**, **`Green Taxis`** y **`FHV - High Volume`**.
- Mala calidad de datos del dataset **`FHV - Others`**.
- La mayoría de los viajes son con un único pasajero.
- 82% de los viajes se realizan bajo el licenciamiento del tipo FHV - High Volume (empresas como Uber)
- Se observa que sólo el 2% de los viajes son compartidos. 
- Las correlaciones más elevadas son entre:
    - trip_distance con fare_amount y total_amount
    - trip_duration con fare_amount y total_amount
- Los Borough de mayor actividad son Mahattan y Brooklyn.
- Los findes de semana (viernes, sábados y domingos) hay mayor cantidad de viajes.
    - En días Laborables la mayor cantidad de viajes sucede a las 08.00 horas y a las 18.00 horas conicendete con los horarios de entrada y salida laboral.
    - En días No Laborables la mayor cantidad de viajes es durante la tarde entre las 15.00 y 18.00 horas.
- En días Laborables la duración de los viajes se incrementa  06.00 y 08.00 horas y principalmente entre las 15.00 y 18.00 horas conicendete con los horarios de entrada y salida laboral.
- La duración promedio de los viajes es menor en días No Laborables.
- En días No Laborables el máximo diurno está entre las 05.00 y 06.00 horas y durante la tarde entre las 14.00 y 17.00, desfazado una hora respecto de los días laborables.
- En días Laborables el precio medio se incrementa de 08.00 a 18.00 horas.
- En días No Laborables el precio medio es mayor durante la madrugada respecto de días No Laborables.
- El medio de pago más utilizado es el Tarjeta de Crédito


---
## Datasets de datos de Viajes Mensual

Los datos se obtienen de la web de la [Comisión de Taxis y Limusinas (TLC)](https://www.nyc.gov/site/tlc/about/aggregated-reports.page).

Se analizó el set de datos en el notebook [EDA Viajes Mensual](./EDA_Viajes_Mensual.ipynb).

[Diccionario de Datos](../../datasets/1.%20Originales/dictionarys/Diccionario%20de%20Datos.xlsx)

- Buena calidad de datos. 
- Se renombraron campos para mantener uniformidad de criterios.
- Se corrigeron "-" como nulos, "," como separadores de miles y tipos de datos. 
- No se observan outliers.

### Conclusiones
- Se observa el fenómeno de la pandemia durante el año 2020 en la cual se produjo una gran reducción de todas las variables que aún no se ha recuperado.
- En cuanto a cantidad de conductores y vehículos, si bien no se ha alcanzado el nivel pre-pandemia, los niveles son más cercanos.
- Se puede concluir que un análsis de series temporales podría proyectarse desde el año 2021 en adelante para evitar el sesgo de pandemia.
- Se puede ver como la cantidad de viajes, conductores y vehículos de la categoría FHV - High Volume es la que empieza a liderar el mercado desde que hay datos en el año 2015.
- No hay información de la facturación de la industria FHV.
- Se observa el crecimiento constante de la cantidad de pagos realizados con tarjeta de crédito.


<p align="center">
<img src="../../Images/Evolución Temporal 1.png"   style="max-width: 100%; height: auto;">
</p>

<p align="center">
<img src="../../Images/Evolución Temporal 2.png"   style="max-width: 100%; height: auto;">
</p>


---
## Datasets de Contaminación y Calidad del Aire

Se analiza un Informe resumido del índice de calidad del aire de AirData, el cual muestra un resumen anual de los valores del índice de calidad del aire (AQI) para 27 condados de Nueva York. El índice de calidad del aire es un indicador de la calidad general del aire, ya que tiene en cuenta todos los contaminantes del aire medidos dentro de un área geográfica. Cuanto más alto sea el valor del AQI, mayor será el nivel de contaminación del aire y mayor será el riesgo para la salud. Se analiza la cantidad de días que fueron categorizados según el AQI. Asimismo se analiza  la cantidad de días que cada contaminante afecto en mayor medida en el periodo analizado. (Ej. Días CO: muestra la cantidad de días en el que CO fue el contaminante principal).

Se analizó el set de datos en el notebook [EDA Air Quality + Emission CO2](./EDA_AirQuality+EmissionCO2.ipynb).

[Diccionario de Datos](../../datasets/1.%20Originales/dictionarys/Diccionario%20de%20Datos.xlsx)

### Conclusiones

#### Impacto a corto plazo - Calidad del Aire
- Dataset se consolido manualmente a partir de la información disponible de [EPA: Enviromental Protection Agency](https://www.epa.gov/outdoor-air-quality-data/air-quality-index-report).
- No hay duplicados ni nulos.
- El índice de calidad del aire es un indicador de la calidad general del aire, ya que tiene en cuenta todos los contaminantes del aire medidos dentro de un área geográfica. Cuanto más alto sea el valor del AQI, mayor será el nivel de contaminación del aire y mayor será el riesgo para la salud.
- Se puede observar el AQI tuvo un importante incremento desde 2022 a 2023.
- Se observa que la mayor cantidad de días son "Buenos" y "Moderados", por sobre los días "No saludables" y "Peligrosos".
    - Días Buenos: Han disminuido notablemente en el último año bajo análisis.
    - Días Moderados: Se ha incrementado en el último período, posiblemente a causa de la disminución de días Buenos.
    - Días Insalubres: En 2023 ha aumentado 5 veces respecto del año anterior.
    - Días Muy Insalubres: Si bien se mantenía en cero desde 2019 a 2022 se incrementaron notablemnte en el 2023. 
    - Días Peligrosos: Mantiene su tendencia en 0.
- PM2.5 y O3 sonn los contaminantes principales.
- Queens es el Borough con un promedio mas alto de AQI máximo y Kings es el que tiene un promedio menor.

#### Impacto a largo plazo - Emisiones de CO2
- El Daset se obtuvo de los datos disponibles en la web de ["Mayor's Office of Climate & Enviromental Justice"](https://climate.cityofnewyork.us/initiatives/nyc-greenhouse-gas-inventories/)
- Se utilizan sólo las columnas de cantidad de CO2 Equivalente para el periodo 2010 a 2022.
- Durante los últimos 3 años, si bien hubo una caída en 2020 por la pandamia, se puede ver un evolución incrementan en 2021 y 2022.
- Si bien se puede notar que el Sector que más impacta en la generación de CO2 es "Energía", el "Transporte" en general es el segundo mayor generador con el 30% del total.
- El transporte de pasajeros (particulares como taxis) es ampliamente superior en la generación de CO2 por su volumen, superando ampliamente los 12 Mill de toneladas.

<p align="center">
<img src="../../Images/Evolución Temporal 3.png"   style="max-width: 100%; height: auto;">
</p>


---
## Datasets de vehículos que utilizan energás alternativas y autos eléctricos

Este proyecto se centra en el análisis exploratorio de datos de un conjunto de datos relacionado con vehículos de combustible alternativo y coches eléctricos. El objetivo es entender mejor las características y tendencias de estos vehículos, incluyendo el año del modelo, la eficiencia, relación precio autonomía y modelos disponibles.

### Dataset de Vehiculos Alternativos

Se analizó el set de datos en el notebook [EDA Alternative Cars](./EDA_alternativecars.ipynb).

[Diccionario de Datos](../../datasets/1.%20Originales/dictionarys/Diccionario%20de%20Datos.xlsx)

- Se analizaron y corrigieron tipos de datos, nulos, duplicados y outliers.
- La calidad de los datos de este dataset no es tan bueno, dado que si bien hay solo una fila duplicada, hay numerosos valores nulos y faltantes. A su vez se observa que hay columnas que no serán necesarias para el trabajo que estamos realizando. Por ello se realizará un ETL para descartar datos irrelevantes.


#### Conclusiones

- Los vehículos de los que más modelos se tiene de acuerdo a la carrocería son los SEDAN/WAGON y SUV, que son en general autos espaciosos pero a su vez no tan grandes. 
- En cuanto al top 10 de fabricantes de vehículos notamos tanto marcas caracterizadas por fabricar vehículos de lujo como así también algunas que son de acceso masivo. El número 1 de hecho es un fabricante de autos que usa todo tipo de publico americano, Ford. 
- Respecto de la distribución de acuerdo al tipo de energía utlizada, se nota una claro liderazgo de los autos eléctricos, en primero lugar electricos híbridos pero le siguen los eléctricos puros y los enchufables. Luego le siguen energias alternativas renobables como: biodisel, etanol e hidrógeno. En menor medida aparecen múltiples variantes de combustibles no renovables como energía, principalmente alrededor del gas natural (GNC).
- En cuanto a la eficiencia de vehículos que usan energía convencional vs los alternativos en carreteras, en ciudades, autopistas y combinadas, es más efiuciente el auto eléctrico aunque en lo que se refiere a ciudad la diferencia es muy leve.

**Economía de Combustible:** Mide la eficiencia con la que un vehículo utiliza el combustible para recorrer una distancia. Se expresa en millas por galón (mpg) o litros por cada 100 kilómetros (L/100 km). Ej: Un auto con una economía de combustible de 30 mpg puede recorrer 30 millas con un galón de gasolina.

<p align="center">
<img src="./../Images/economia_de_combustible.png"   style="max-width: 100%; height: auto;">
</p>


### Dataset de Vehiculos Eléctricos

Se analizó el set de datos en el notebook [EDA Alternative Cars](./EDA_alternativecars.ipynb).

[Diccionario de Datos](../../datasets/1.%20Originales/dictionarys/Diccionario%20de%20Datos.xlsx)

- Se analizaron y corrigieron tipos de datos, nulos, duplicados y outliers.
- La calidad de los datos de este dataset es muy bueno. No hay filas duplicadas, ni datos nulos y a excepción de un solo dato, FastCharge_KmH, el resto tenían el tipo de dato adecuado para su análisis. A su vez se observa que hay columnas que no serán necesarias para el trabajo que estamos realizando. Por ello se realizará un ETL para descartar datos irrelevantes.
- Se observaron pocos outliers, pero se concluyó que probablemente se deba a son datos atípicos respecto de los demás, pero correctos. Por ejemplo en el boxplot de precio, hay unos pocos datos muy por encima del precio de los demás, pero eso se debe a que entre los modelos del dataset hay autos de muy alta gama, que lógicamente tendrán un precio muy diferente.

#### Conclusiones

- En cuanto al top 10 de marcas fabricantes de vehiculos existe un claro líder que es Tesla mientras que Ford ya aprece en el último puesto de esta lista pero hay más presencia de marcas más populares que en el otro dataset.
- En relación al promedio del precio de un vehiculo por marca, se observa que las marcas de lujo tienen un precio promedio por encima de los 100.000 euros, mientras que hay modelos con precios en promedio más acequibles, rondando la mayoría valores entre 20.000 y 40.000 euros en promedio.
- En sintonía con lo analizado en el dataset de autos de energías alternativas, vemos que los vehículos de los que más modelos se fabrica de acuerdo a la carrocería son los SUV y Hatchback, a la cabeza y ya más relegado vienen los SEDAN.

- En cuanto a la relación Eficiencia Energética / Autonomía en función del precio, hay una correlación positiva, donde los vehículos con mayor eficiencia energética (menor consumo de Wh/km) y autonomía, tienden a ser más caros. 

<img src="../../Images/precio_autonomia.png"  style="max-width: 100%; height: auto;"/>