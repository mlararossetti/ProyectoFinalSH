# Proyecto de Machine Learning: Predicción de Series de Tiempo

**Dataset de Entrenamiento**

Utilizando un dataset depurado de Taxis de Nueva York mensuales, se construyó un modelo de serie tiempo para la predicción de ciertas variables del negocio.

Este proyecto tiene como objetivo realizar una proyección del mercado para el análisis de la inversión en la industria de taxis usando modelos de series de tiempo. Se utilizó **Prophet** para construir un modelo que permita proyectar valores futuros con base en datos históricos.

## Objetivos

Este proyecto tiene como objetivo predecir diferentes métricas de la industria de taxis en Nueva York utilizando modelos de series de tiempo. Para ello, empleamos datos históricos y la biblioteca Prophet, optimizando parámetros para mejorar la precisión de las predicciones.

## Requisitos

- **Prophet**: Modelado de series temporales
- **Python**: Para análisis y desarrollo
- **pandas**: Manipulación y análisis de datos
- **numpy**: Manipulación y análisis de datos
- **plotly**: Visualización de datos
- **matplotlib**: Visualización de datos

### Prophet:

Es una biblioteca de código abierto desarrollada por Facebook para la previsión de series temporales. Hemos elegido esta biblioteca porque:

1. Facilidad de uso: La sintaxis es intuitiva y se puede integrar fácilmente con bibliotecas de Python, lo cual en nuestra curva de aprendizaje se vuelve de gran relevancia.
2. Manejo de estacionalidades y tendencias: Prophet asimila datos de series de tiempo con estacionalidad múltiples y genera una proyección con un margen de error aceptable.
3. Manejo de datos faltantes y outliers: Puede manejar datos ruidosos sin necesidad de un preprocesamiento exhaustivo.
4. Escalabilidad: para trabajar con grandes conjuntos de datos y múltiples series temporales.
5. Resultados interpretables: Los resultados son fáciles de leer y analizar.

## Contenido del Proyecto

**Productos Finales**

1. Modelo Entrenado:

- Guardado en formato .joblib para su reutilización.
- Parametrizado según tipo de industria y columna de interés.

2. Predicciones:

- Archivo .csv con resultados del pronóstico.
- Gráficas interactivas para visualización del pronóstico y comparación con datos históricos.

3. Notebooks:

- ML_Time_Series_SIN_CV.ipynb: Es el inicio del flujo de trabajo, donde se cargan datos, se visualizan tendencias iniciales y se prepara el modelo para predicción sin validación cruzada.
- ML_Time_Series_SIN_CV_ENTRENADO.ipynb: Continuación más avanzada, que incluye un modelo entrenado y optimizado.

### Carga de datos:

- Para el modelo final, los datos se cargan desde un archivo CSV que contiene un subdataset depurado con el fin de usarlo para el modelo en particular (`TLC Aggregated Data\ML_TS_Input.csv`), filtrados por tipo de industria y variable a predecir, los cuales se seleccionan mediante inputs en el código.
- Se trabajó con un archivo consolidado que contiene métricas como total_trips, total_co2_emission y avg_trip_distance.
- Se establece el período máximo de predicción y se calcula los meses necesarios para trabajar con el modelo.
- Se asegura que solo se trabajen valores no negativos para mantener la coherencia de los datos.
- Se crea una función que guarde las predicciones en un csv.

### Dataset de Entrenamiento

A partir del dataset original preprocesado, que incluye información como fecha, tipo de transporte, número de viajes y tarifas recolectadas, se construye un subconjunto organizado para el entrenamiento del modelo. Este dataset incluye las siguientes columnas principales:

- date: Fecha del registro.
- industry: Tipo de industria o transporte.
- total_trips: Total de viajes realizados.
- avg_trip_distance: Distancia promedio por viaje.
- total_amount: Total facturado.
- avg_amount_per_trip: Facturación promedio por viaje.
  El procesamiento inicial del dataset y la organización de las columnas se detalla en los notebooks incluidos en el repositorio.

## Cómo ejecutar el proyecto

En esta etapa, para ejecutar el análisis y realizar predicciones, el usuario podrá realizarse dichas acciones directamente desde una botonera interactiva desarrollada en Streamlit.

### Selección de parámetros:

El modelo se encuentra configurado para predicciones automáticas. Los usuarios pueden seleccionar:

1. La columna objetivo a predecir (e.g., total_trips, avg_trip_distance).
2. El horizonte de predicción deseado (e.g., cantidad de meses).
3. Opcionalmente, ajustar hiperparámetros para mejorar el rendimiento del modelo.
   Las predicciones se guardan en un archivo .csv y se visualizan mediante gráficas interactivas generadas en los notebooks.

### Preparación de los datos:

- Los datos son procesados para cumplir con el formato que requiere Prophet, renombrando las columnas necesarias (`ds` para la fecha y `y` para la métrica).

### Visualización de datos históricos:

- Se genera un gráfico interactivo de los datos históricos seleccionados usando Plotly, lo que permite observar la tendencia inicial de la métrica seleccionada.

### Predicción de la serie de tiempo:

- Se configura el modelo de Prophet para incluir una estacionalidad mensual y modo aditivo.
- El modelo realiza una predicción, y los resultados se muestran en un gráfico con los valores históricos, la predicción, y el intervalo de confianza.

### Entrenamiento y Validación

El modelo se entrena con los datos preprocesados del dataset y se evalúa mediante validación cruzada. En este proceso, se "esconden" valores conocidos para compararlos con las predicciones realizadas, cuantificando la precisión del modelo.
Se probaron diferentes configuraciones de los parámetros changepoint_prior_scale y seasonality_prior_scale.
Se ajustaron estacionalidades aditivas y multiplicativas según las características de cada métrica.

### Evaluación:

Las métricas utilizadas para evaluar el rendimiento incluyen:

- MSE (Mean Squared Error): mide el promedio de los errores al cuadrado entre las predicciones y los valores reales. Penaliza más los errores grandes debido a la cuadratura.
- RMSE (Root Mean Squared Error): es la raíz cuadrada del MSE y está en la misma escala que los valores originales, lo que facilita la interpretación.
- MAE (Mean Absolute Error): mide el error promedio entre las predicciones y los valores reales, tomando la media de las diferencias absolutas.
- MAPE (Mean Absolute Percentage Error): mide el error promedio entre las predicciones y los valores reales en términos de porcentaje, útil para comparar la precisión de modelos en diferentes escalas ya que normaliza los errores.

Se realiza además una búsqueda de hiperparámetros mediante Grid Search para optimizar el modelo y mejorar la precisión de las predicciones.

### Análisis de componentes y Visualización de resultados:

- Se genera un análisis de los componentes del modelo de predicción, permitiendo observar las tendencias y estacionalidades capturadas.
- Se generaron gráficos interactivos para explorar tendencias y predicciones.

### Guardado de predicciones:

- Finalmente, se guardan los resultados de la predicción en un archivo CSV.

### Conclusiones

- El modelo desarrollado proporciona un pronóstico confiable para datos de series temporales en transporte. Aunque sujeto a futuras mejoras, presenta una base robusta para predecir métricas clave y apoyar la toma de decisiones estratégicas.
- Prophet ofrece una gran flexibilidad para trabajar con datos estacionales, pero su rendimiento depende altamente de la selección adecuada de parámetros.
- Es crucial manejar correctamente datos faltantes y outliers, ya que afectan directamente la calidad de las predicciones.
- Ajustar estacionalidades (aditivas vs multiplicativas) según las características de la métrica puede mejorar significativamente el modelo.
