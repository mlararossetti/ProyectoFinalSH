# Modelo de Machine Learning: Predicción de Series de Tiempo

## Objetivo

El objetivo es entrenar un modelo de ML de series de tiempo que realice una proyección de las variables de mercado necesarias para el análisis de la inversión en la industria de taxis de New York. Para esto se utilizó la librería **Prophet**, optimizando los hiperparámetros para mejorar la precisión de las predicciones.


## Dataset de Entrenamiento

Se utilizó el dataset depurado de Taxis de Nueva York con agregación mensual resultante del proceso de carga incremental desarrollado en la Google Cloud y se construyó un modelo de serie tiempo para la predicción de variables del negocio requeridas para el flujo de fondos.


### Carga de datos:

- Los datos de entrada al modelo surgen de el [`ETL_ML_Time_Series`](/notebooks/1.%20ETL/ETL_ML_Time_Series.ipynb) que se encarga de disponibilizar la información en el archivo [`ML_TS_Input.csv`](../datasets/2.%20Depurados/TLC%20Aggregated%20Data/ML_TS_Input.csv) el cual contiene un la un dataset depurado, filtrado por tipo de industria y variable a predecir. Además crea un tipo de industria "Total Mercado" para evaluar la evolución del mercado globalmente.

- Este archivo contiene la siguiente información:
  - date: mes/año del registro.
  - industry: tipo de industria (Yellow Taxis, Green Taxis, FHV - HV, FHV - Other y Total Mercado)
  - total_trips: total de viajes realizados por mes
  - avg_trip_distance: distancia promedio por viaje.
  - total_amount: total facturado por mes.
  - total_co2_emission: emisión total de CO2 por mes.
  - unique_vehicles: cantidad de vehículos en circulación en el mercado.

## Modelo utilizado

Prophet es una biblioteca de código abierto desarrollada por Meta para la previsión de series temporales. Hemos elegido esta biblioteca por:

1. Facilidad de uso: buen rendimiento con series de tiempo y relativa sencillez de implementación para series temporales simples como las que diponemos. 
2. Manejo de estacionalidades: Prophet asimila datos de series de tiempo con estacionalidad múltiples y genera una proyección con un margen de error aceptable.
3. Resultados interpretables: Los resultados son fáciles de leer y analizar.


## Contenido del Proyecto


### Entrenamiento

En el notebook `ML_Time_Series.ipynb`:

- Se entrena el modelo dividiendo el dataset en un set de entrenamiento con información desde 2021-01-01 hasta 2023-08-01 y un set de test que incluye el período 2023-09-01 a 2024-08-01.
- El modelo realiza una predicción y los resultados se muestran en un gráfico con los valores históricos, la predicción y el intervalo de confianza.
- Se realiza un Grid Search con distintos valores de los hiperparámetros (`changepoint_prior_scale`, `seasonality_prior_scale`, `seasonality_mode`) y se busca el mejor resultado para cada industria y variable. 
- Se elimina la estacionalidad semanal y se mantiene la estacionalidad anual dado que los datos son mensuales.
- Para la evaluación de resultados se miden los errores del modelo para el periodo de test:
  - MSE (Mean Squared Error): mide el promedio de los errores al cuadrado entre las predicciones y los valores reales. Penaliza más los errores grandes debido a la cuadratura.
  - RMSE (Root Mean Squared Error): es la raíz cuadrada del MSE y está en la misma escala que los valores originales, lo que facilita la interpretación.
  - MAE (Mean Absolute Error): mide el error promedio entre las predicciones y los valores reales, tomando la media de las diferencias absolutas.
  - MAPE (Mean Absolute Percentage Error): mide el error promedio entre las predicciones y los valores reales en términos de porcentaje, útil para comparar la precisión de modelos en diferentes escalas ya que normaliza los errores.
- Se evaluan los tiempos de entrenamiento de los modelos.
- La totalidad de los resultados se guardan en [`todos_los_resultados_modelos.csv`](/Modelos%20de%20ML/todos_los_resultados_modelos.csv) y los mejores resulados se guardan en [`mejores_modelos.csv`](/Modelos%20de%20ML/mejores_modelos.csv).

En el notebook `ML_Time_Series_Entrenado.ipynb`:
- A partir de la configuración de los hiperparámetros resultantes para la minimización de los errores se levantan los modelos y se los entrena.
- Se analizan los resultados a partir de un selector: de industria, variable y cantidad de periodos mensuales a pronosticar.
  - Industry:  Yellow Taxis, Green Taxis, FHV - HV, FHV - Other y Total Mercado
  - Variables: total_trips, unique_vehicles, total_amount, avg_trip_distance, 'total_co2_emission'
  - El horizonte de predicción deseado (e.g., cantidad de meses).
- Este notebook se encarga de guardar los modelos finales entrenados en utilizando la librería `joblib` que luego minimizarán los tiempos de consumo en Streamlit.
- Adicionalmente generan un archivo de salida  [`ML_TS_Output.csv`](../datasets/2.%20Depurados/TLC%20Aggregated%20Data/ML_TS_Output.csv) con los valores de las previsiones realizadas para ser consumidas por el Modelos de Flujo de Fondos.



## Productos Finales

1. Modelos entrenados:
    - Guardado en formato `.pkl` con la librería `joblib` para su reutilización.
    - Mejores parametrizaciones del modelo según tipo de industria y la variable de interés.

2. Predicciones:
    - Archivo [`ML_TS_Output.csv`](../datasets/2.%20Depurados/TLC%20Aggregated%20Data/ML_TS_Output.csv) con resultados del pronóstico optimizado.
    - Gráficas interactivas para visualización del pronóstico y comparación con datos históricos.

## Conclusiones

- Los pronósticos por tipo de industria nos permiten identificar las siguientes características de mercado fundamentales para el desarrollo del proyecto de negocios:
  - FHV - High Volume es la industria que mejor pronóstico de evolución de mercado tiene, tanto en lo relativo a cantidad de viajes como a monto de facturación. Esto hace que sea el objetivo de ingreso para nuestro cliente al mercado.
  - Las demás industrias muestran cantidad de viajes y facturación estabilizadas en los valores actuales sin tendencia definida de crecimiento o decrecimiento.
- El modelo desarrollado proporciona un pronóstico confiable para datos de series temporales en transporte. Aunque sujeto a futuras mejoras, presenta una base robusta para predecir métricas clave y apoyar la toma de decisiones estratégicas.
- Prophet ofrece una gran flexibilidad para trabajar con datos estacionales, pero su depende altamente de la selección adecuada de parámetros.



## Requisitos

- **Prophet**: Modelado de series temporales
- **Python**: Para análisis y desarrollo
- **pandas**: Manipulación y análisis de datos
- **numpy**: Manipulación y análisis de datos
- **plotly**: Visualización de datos
- **matplotlib**: Visualización de datos