import streamlit as st
import pandas as pd 
import numpy_financial as npf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.title('Flujo de fondos de la flota elegida')

future_data = pd.read_csv("datasets/2. Depurados/TLC Aggregated Data/ML_TS_Output_Anualized.csv")
future_data = future_data[future_data['industry']=='FHV - High Volume']

future_data.rename(columns={
    'anual_income_per_vehicle': 'Income_per_Vehicle (USD)',
    'anual_distance_per_vehicle': 'Miles_per_Vehicle',
    'anual_total_co2_emission': 'Total_CO2_Emissions'
}, inplace=True)
future_data =  future_data[future_data['year']>=2025]

# Dataset de VE
df_autos = pd.read_csv('datasets/2. Depurados/ElectricCarData_Clean.csv')#"df_modelo.csv")
df_autos.rename(columns={
    'brand': 'Brand',
    'model': 'Model',
    'efficiency_whkm': 'Efficiency (Wh/km)'
}, inplace=True)

df_autos['Efficiency (kWh/mile)'] = df_autos['Efficiency (Wh/km)']/1000* 0.1688666667 
df_autos['Precio Dolar'] = df_autos['price_euro'] * 1.06

promedio_ingresos = round(future_data["Income_per_Vehicle (USD)"].mean(),2)
promedio_millas = round(future_data["Miles_per_Vehicle"].mean(),2)
#print(f'El promedio de ingresos anuales es: {promedio_ingresos}')
#print(f'El promedio de millas recorridas anualmente es : {promedio_millas}')

año = 2025
for _, row in future_data.iterrows():  # iterrows() en lugar de interrows()
    globals()[f'Ingresos_año_{año}'] = round(row["Income_per_Vehicle (USD)"],2)
    #print(f'Los ingresos para el año {año} son {globals()[f"Ingresos_año_{año}"]}')
    año += 1

ingresos_años = []
for _, row in future_data.iterrows():
    ingresos_años.append(round(row["Income_per_Vehicle (USD)"],2))
#print(ingresos_años)

año = 2025
for _, row in future_data.iterrows():
    globals()[f'Millas_Año_{año}'] = round(row["Miles_per_Vehicle"],2)
    #print(f'Las Millas recorridas en el año {año} son {globals()[f"Millas_Año_{año}"]}')
    año+=1

millas_años = []
for _, row in future_data.iterrows():
    millas_años.append(round(row["Miles_per_Vehicle"],2))
#print(millas_años)


class Auto:
    def __init__(self,tasa_descuento, precio, iva, licencia_1, licencia_2, placa, inspeccion, seguro, recorrido_anual, 
                 ingresos_anuales):
        self.precio = precio
        self.iva = iva
        self.licencia_1 = licencia_1
        self.licencia_2 = licencia_2
        self.placa = placa
        self.inspeccion = inspeccion
        self.seguro = seguro
        self.recorrido_anual = recorrido_anual
        self.ingresos_anuales = ingresos_anuales
        self.tasa_descuento = tasa_descuento
    
    def inversion_inicial(self):
        raise NotImplementedError
    
    def costos_operativos(self):
        raise NotImplementedError
    
    def flujo_neto_anual(self):
        return self.ingresos_anuales - self.costos_operativos()
    
    def flujo_caja_proyectado(self, años=7):
        
        # Inversión inicial negativa porqué es el año 0
        inversion_inicial = -self.inversion_inicial()
        
        ingresos_año = [0]
        costos_año = [0]
        flujo_neto = [inversion_inicial]  # Año 0: 
        flujo_descuento = [inversion_inicial]  # Año 0 Inversión inicial negativa
        ingresos_descuento_año = [0]
        
        # Se calcula el flujo neto anual
        for año in range(1, años + 1):
            self.ingresos_anuales = ingresos_años[año-1]
            self.recorrido_anual = millas_años[año-1]
            flujo_neto_actual = self.flujo_neto_anual()
            flujo_neto.append(flujo_neto_actual)
            flujo_descuento_actual = flujo_neto_actual / (1 + self.tasa_descuento) ** año
            flujo_descuento.append(flujo_descuento_actual)
            ingresos_año.append(self.ingresos_anuales)
            ingresos_descuento_año.append(ingresos_años[año-1]  / (1 + self.tasa_descuento) ** año)
            costos_año.append(self.costos_operativos())
        
        # Se crea el DataFrame de resultados
        df_flujo_caja = pd.DataFrame({
            'Año': range(0, años + 1),
            'Ingresos': ingresos_año, 
            'Costos Operativos': costos_año,
            'Flujo Neto': flujo_neto,
            'Flujo Neto Descontado': flujo_descuento,
            'Ingresos Descontado': ingresos_descuento_año        
        })
        
        # Calculo el flujo total descontado para el ROI
        return df_flujo_caja

    def calcular_roi(self, flujo_total):
        roi = flujo_total/ self.inversion_inicial() *100
        roi_mensual_simple = roi/7/12
        #roi_mensual_compuesto = ((1+ flujo_total/ self.inversion_inicial())**(1/(7*12))-1)*100 #- self.inversion_inicial()
        return round(roi, 2),round(roi_mensual_simple, 2)#,round(roi_mensual_compuesto, 2)

    def calcular_ir(self, ingreso_total):
        ir = ingreso_total / abs(self.inversion_inicial())
        return round(ir, 2)

    def calcular_payback_period(self):
        flujo_acumulado = 0
        payback = 0
        for año in range(1, 8):
            flujo_anual = self.flujo_neto_anual()
            flujo_acumulado += flujo_anual
            if flujo_acumulado >= abs(self.inversion_inicial()):
                payback = año
                break
        return payback if payback > 0 else "No recuperado en 7 años"

class AutoConvencional(Auto): #Licencia_1 = unico pago, licencia_2 = anual
    def __init__(self, tasa_descuento, precio=36200, iva=0.08875, licencia_1=550,licencia_2=100, placa = 300,
                 seguro=5000, inspeccion = 150,
                 eficiencia=25 , mantenimiento=0.15, recorrido_anual=promedio_millas, #eficiencia en MPG / mantenimiento = USD x Milla
                 ingresos_anuales=promedio_ingresos):
        super().__init__(tasa_descuento,precio, iva, licencia_1, licencia_2, placa, inspeccion,
                         seguro, recorrido_anual, ingresos_anuales) # Se usa el super constructor para evitar redundancia ya que es una clase hija
        self.eficiencia = eficiencia
        self.mantenimiento = mantenimiento
    
    def inversion_inicial(self):
        return self.precio * (1 + self.iva) + self.licencia_1
    
    def costos_operativos(self):
        precio_gasolina_galon = 3.06 #USD x galon
        costo_gasolina_anual = (self.recorrido_anual / self.eficiencia) * precio_gasolina_galon
        costo_mantenimiento = self.mantenimiento * self.recorrido_anual
        costo_anual_salario = 2342 * 20  # Precio medio de la hora de un conductor de autos convencionales.
        return costo_gasolina_anual + costo_mantenimiento + self.seguro + self.licencia_2 + self.placa + self.inspeccion + costo_anual_salario

def calcular_metricas_flota(tasa_descuento, cantidad_ve, cantidad_conv):
    resultados = []
    flujo_neto_comb_lista = []
    for _, fila in df_autos.iterrows():
        # Se extraen los datos del Dataset
        marca = fila['Brand']
        modelo = fila['Model']
        tipo_de_auto = fila['body_style']
        segmento = fila['segment']
        precio_ve = fila['Precio Dolar']
        eficiencia_ve = fila['Efficiency (kWh/mile)']
        eficiencia_conv = 25

        eficiencia_total = (33.7 /  eficiencia_conv * cantidad_conv + eficiencia_ve * cantidad_ve) / (cantidad_ve+cantidad_conv)

        # Se instancian los autos segun su naturaleza (electrico o convencional)
        auto_electrico = AutoElectrico(tasa_descuento, precio=precio_ve, eficiencia=eficiencia_ve)
        auto_convencional = AutoConvencional(tasa_descuento)


        # Se calcula el flujo de caja proyectado para cada tipo de auto
        flujo_ve = auto_electrico.flujo_caja_proyectado()
        flujo_conv = auto_convencional.flujo_caja_proyectado()
        flujo_neto_comb_lista =  cantidad_ve * flujo_ve['Flujo Neto Descontado'] +  cantidad_conv  * flujo_conv['Flujo Neto Descontado']

        # Se combinar flujos de caja para la flota (teniendo en cuenta su respectiva cantidad)
        flujo_neto_comb = round(
            cantidad_ve * flujo_ve['Flujo Neto Descontado'].sum() +
            cantidad_conv * flujo_conv['Flujo Neto Descontado'].sum(), 2
        )
        
        ingreso_comb =  round(
            cantidad_ve * flujo_ve['Ingresos Descontado'].sum() +
            cantidad_conv * flujo_conv['Ingresos Descontado'].sum(), 2
        )

        # Se calcula  la inversión inicial combinada
        inversion_comb = round(
            cantidad_ve * auto_electrico.inversion_inicial() +
            cantidad_conv * auto_convencional.inversion_inicial(), 2
        )
        
        # Se calcular las métricas financieras combinadas
        roi_comb = flujo_neto_comb/ inversion_comb *100 / 7
        #roi_mensual_simple = roi_comb/12
        ir_comb = ingreso_comb / abs(inversion_comb)
        tir_comb = round(npf.irr(flujo_neto_comb_lista)*100,2)

        # Calculo del payback period combinado (considerando la proporción)
        flujo_anual_comb = [
            cantidad_ve * flujo_ve['Flujo Neto'].iloc[año] +
            cantidad_conv * flujo_conv['Flujo Neto'].iloc[año]
            for año in range(1, 6)
        ]
        flujo_acumulado = 0
        payback_comb = 0
        for año, flujo in enumerate(flujo_anual_comb, start=1):
            flujo_acumulado += flujo
            if flujo_acumulado >= abs(inversion_comb):
                payback_comb = año
                break
        
        # Se almacenan los resultados para el modelo actual
        resultados.append({
            'Brand': marca,
            'Model': modelo,
            'Tipo de Auto': tipo_de_auto,
            'Segmento':segmento,
            'Efficiency Total (kWh/mile)' : round(eficiencia_total,4),
            'Inversión Inicial Total (USD)': round(inversion_comb,0),
            #'Relación Inversión/Eficiencia (USD.mile/kWh)': round (inversion_comb/eficiencia_total,2),
            'VNA (USD)': round(flujo_neto_comb,0),
            'TIR (%)':round(tir_comb,2),
            'ROI Anual (%)': round(roi_comb,2),
            #'ROI Mensual(%)': round(roi_mensual_simple,4),
            'IR (USD)': round(ir_comb,2),
            'Payback Period (Años)': payback_comb if payback_comb > 0 else "No recuperado en 7 años"
        })

    # Se convertierten los resultados a tipo DataFrame para una mejor visualización
    df_resultados = pd.DataFrame(resultados)
    df_resultados = df_resultados.sort_values(by="ROI Anual (%)", ascending=False).reset_index(drop=True) # Se ordena para tener el ranking 


    return df_resultados


class AutoElectrico(Auto): #Descuento de 5% al 10% en licencia ; Excencion del impuesto de venta
    def __init__(self,tasa_descuento, precio, eficiencia, iva=0, licencia_1=495,licencia_2=100, placa = 300,
                 seguro=1500, inspeccion = 100, mantenimiento=0.03, wallbox=600, 
                 recambio_bateria=5000, #mantenimiento = USD x Milla
                 recorrido_anual=promedio_millas, ingresos_anuales=promedio_ingresos): 
        super().__init__(tasa_descuento, precio, iva, licencia_1, licencia_2, placa, inspeccion, seguro, recorrido_anual, 
                         ingresos_anuales)
        self.eficiencia = eficiencia
        self.mantenimiento = mantenimiento
        self.wallbox = wallbox
        self.recambio_bateria = recambio_bateria
        self.tasa_descuento = tasa_descuento
        self.licencia_1=licencia_1
    
    def inversion_inicial(self):
        return self.precio + self.licencia_1 + self.wallbox
    
    def costos_operativos(self):
        precio_electricidad_kWh = 0.13 #USD x kHw
        costo_electricidad_anual = (self.recorrido_anual * self.eficiencia) * precio_electricidad_kWh
        costo_mantenimiento = self.mantenimiento * self.recorrido_anual
        costo_anual_bateria = self.recambio_bateria / 12.5
        costo_anual_salario = 2342 * 22 # Promedio de horas de menejo de un conductor por año * Precio promedio de la hora de un chofer de taxis en NY para VE.
        return costo_electricidad_anual + costo_mantenimiento + costo_anual_bateria + self.seguro + self.licencia_2 + self.placa + self.inspeccion + costo_anual_salario

# Primer Parámetro : Cantidad VE; Segundo Parámetro : Cantidad Autos Convencional
# Crear un selector para la cantidad de autos
cantidad_ve = st.slider("Seleccione cantidad de autos eléctricos:",min_value=1, max_value=1500, step=1)
cantidad_conv = st.slider("Seleccione cantidad de autos convencionales:",min_value=0, max_value=1500, step=1)
tasa_desc = st.slider('Seleccione la tasa de descuento %', min_value=5, max_value = 15, step = 1)
tasa_descuento = tasa_desc/100 
resultados_flota = calcular_metricas_flota(tasa_descuento, cantidad_ve, cantidad_conv)
# Obtener los valores únicos y ordenarlos alfabéticamente
tipo_de_auto = sorted(resultados_flota['Tipo de Auto'].unique())
tipo_de_auto.insert(0, "Todos")

segmento = sorted(resultados_flota['Segmento'].unique())
segmento.insert(0, "Todos")

# Crear widgets en Streamlit
tipo_de_auto_selector = st.selectbox('Tipo de Auto:',options=tipo_de_auto)
segmento_selector = st.selectbox('Segmento:',options=segmento)

# Función para filtrar
def filtra(resultados_flota, tipo_de_auto, segmento):
    if segmento == 'Todos':
        if tipo_de_auto == 'Todos':
            resultados_flota = resultados_flota
        else:
            resultados_flota = resultados_flota[resultados_flota['Tipo de Auto'] == tipo_de_auto]
    elif tipo_de_auto == 'Todos':
        resultados_flota = resultados_flota[resultados_flota['Segmento'] == segmento]
    else:
        resultados_flota = resultados_flota[
            (resultados_flota['Tipo de Auto'] == tipo_de_auto) & 
            (resultados_flota['Segmento'] == segmento)
        ]
    return resultados_flota

# Aplicar filtros
tipo_de_auto = tipo_de_auto_selector
segmento = segmento_selector
resultados_flota_aux = resultados_flota.copy()
resultados_flota_aux = filtra(resultados_flota_aux, tipo_de_auto, segmento)
resultados_flota_aux.head(5) 
# head (5) para obtener el Ranking 
# Mostrar el DataFrame resultante
st.write("Tabla de Resultados:")
st.markdown(f"""
En esta tabla se muestran los 5 mejores modelos de vehículos eléctricos en función a su rentabilidad.
A su vez se calculan distintas métricas como Efficiency (kWh/mile), Inversión Inicial Total (USD), VNA(USD), TIR (%), ROI%, ROI% mensualizado, IR(USD) y Payback Period (Años) para la combinación de {cantidad_ve} vehículos eléctricos y {cantidad_conv} vehículos convencionales. 
            """)
# Mostrar el DataFrame resultante
df5 = resultados_flota_aux.head(5)
st.dataframe(df5)

###################### KPIS Y FUNCIONES NUEVAS
actual_data = pd.read_csv('datasets/2. Depurados/TLC Aggregated Data/merged_taxi_data.csv')
max_date = actual_data['date'].max()
actual_data = actual_data[(actual_data['industry']=='FHV - High Volume') & (actual_data['date']==max_date)]

unique_vehicles = actual_data['unique_vehicles'].iloc[0]
total_trips =  actual_data['total_trips'].iloc[0]
avg_trips_per_vehicle = total_trips/unique_vehicles
avg_trip_distance = actual_data['avg_trip_distance'].iloc[0]

CO2_convencional = (cantidad_conv+cantidad_ve) * avg_trips_per_vehicle * avg_trip_distance  * 400 /1000000
CO2_real = (cantidad_conv) * avg_trips_per_vehicle * avg_trip_distance  * 400 /1000000 + cantidad_ve * avg_trips_per_vehicle * avg_trip_distance  * 42 /1000000
ahorro_CO2 = (1 - CO2_real/CO2_convencional) * 100

best_roi = resultados_flota_aux['ROI Anual (%)'].iloc[0]

# Crear gráfico individual para KPI: ROI Anual
def kpi_roi_anual():
    valor_actual = best_roi  # Ejemplo de valor actual
    rango_max = 30
    threshold_value = 8
# Crear el gráfico tipo gauge
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=valor_actual,
        gauge={
            'axis': {'range': [0, rango_max]},  # Rango del indicador
            'bar': {'color': "blue"},  # Color de la barra del indicador
            'steps': [
                {'range': [0, valor_actual], 'color': "lightblue"},  # Rango bajo
                {'range': [valor_actual, rango_max], 'color': "white"}  # Rango alto
            ],
            'threshold': {
                'line': {'color': "darkblue", 'width': 4},  # Línea del valor umbral
                'thickness': 0.75,
                'value': threshold_value  # Valor del umbral
            }
        },
        number={'suffix': "%"},  # Agrega un sufijo de porcentaje al valor
        title={'text': "KPI: ROI Anual"}  # Título del gráfico
    ))

# Agregar una anotación para mostrar el valor del threshold
    fig.add_annotation(
        x=0.5,  # Coordenada x de la anotación (en términos de proporción)
        y=-0,  # Coordenada y de la anotación
        text=f"Objetivo: {threshold_value}%",  # Texto de la anotación
        showarrow=False,  # Sin flecha
        font=dict(size=12, color="darkblue"),  # Estilo del texto
        xanchor="center",  # Anclaje horizontal
        yanchor="top"  # Anclaje vertical
)
    return fig

# Crear gráfico individual para KPI: Proporción por cantidad de autos
# Crear gráfico individual para KPI: Proporción por cantidad de autos
def kpi_proporcion_autos():
    valor_actual = (cantidad_conv + cantidad_ve) / unique_vehicles * 100
    rango_max = valor_actual * 2
    threshold_value = 1

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=valor_actual,
        gauge={
            'axis': {'range': [0, rango_max]},
            'bar': {'color': "rgb(0, 167, 193)"},
            'steps': [
                {'range': [0, valor_actual], 'color': "rgb(4, 144, 158)"},
                {'range': [valor_actual, rango_max], 'color': "white"}
            ],
            'threshold': {
                'line': {'color': "darkblue", 'width': 4},
                'thickness': 0.75,
                'value': threshold_value
            }
        },
        number={'suffix': "%"},
        title={'text': "Proporción de Mercado (Cantidad de Autos)"}
    ))

    fig.add_annotation(
    x=0.5,  # Posición horizontal en coordenadas del gráfico
    y=0,    # Posición vertical
    text=f"Objetivo: {threshold_value}%",  # Texto que se muestra
    showarrow=False,  # Sin flecha
    font=dict(size=12, color="darkblue"),  # Estilo del texto
    xanchor="center",
    yanchor="top")
    return fig

# Crear gráfico individual para KPI: Proporción por cantidad de viajes
def kpi_proporcion_viajes():
    valor_actual = (cantidad_conv + cantidad_ve) * avg_trips_per_vehicle / total_trips * 100
    rango_max = valor_actual * 2
    threshold_value = 1

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=valor_actual,
        gauge={
            'axis': {'range': [0, rango_max]},
            'bar': {'color': "rgb(255, 188, 50)"},
            'steps': [
                {'range': [0, valor_actual], 'color': "rgb(247, 168, 28)"},
                {'range': [valor_actual, rango_max], 'color': "white"}
            ],
            'threshold': {
                'line': {'color': "darkblue", 'width': 4},
                'thickness': 0.75,
                'value': threshold_value
            }
        },
        number={'suffix': "%"},
        title={'text': "Proporción de Mercado (Cantidad de Viajes)"}
    ))

    # Agregar una anotación para mostrar el valor del threshold
    fig.add_annotation(
    x=0.5,  # Posición horizontal en coordenadas del gráfico
    y=0,    # Posición vertical
    text=f"Objetivo: {threshold_value}%",  # Texto que se muestra
    showarrow=False,  # Sin flecha
    font=dict(size=12, color="darkblue"),  # Estilo del texto
    xanchor="center",
    yanchor="top")
    
    return fig

# Crear gráfico individual para KPI: Ahorro de CO2
def kpi_ahorro_CO2():
    valor_actual = ahorro_CO2
    rango_max = 100
    threshold_value = 30

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=valor_actual,
        gauge={
            'axis': {'range': [0, rango_max]},
            'bar': {'color': "rgb(236, 85, 108)"},
            'steps': [
                {'range': [0, valor_actual], 'color': "rgb(226, 61, 93)"},
                {'range': [valor_actual, rango_max], 'color': "white"}
            ],
            'threshold': {
                'line': {'color': "darkblue", 'width': 4},
                'thickness': 0.75,
                'value': threshold_value
            }
        },
        number={'suffix': "%"},
        title={'text': "Ahorro de CO2 respecto de flota convencional"}
    ))

    # Agregar una anotación para mostrar el valor del threshold
    fig.add_annotation(
    x=0.5,  # Posición horizontal en coordenadas del gráfico
    y=0,    # Posición vertical
    text=f"Objetivo: {threshold_value}%",  # Texto que se muestra
    showarrow=False,  # Sin flecha
    font=dict(size=12, color="darkblue"),  # Estilo del texto
    xanchor="center",
    yanchor="top")

    return fig

# Interfaz de Streamlit con columnas
st.subheader("Indicadores Clave de Desempeño (KPIs)")
st.write("Este tablero muestra los KPIs calculados en función de los objetivos propuestos y la flota elegida de vehículos eléctricos y convencionales.")


# KPI: ROI Anual
col1, col2 = st.columns([1, 1], vertical_alignment = 'center')
with col1:
    st.markdown("""  
                  
                  
                **ROI Anual**: Este indicador mide el rendimiento de la inversión anual basado en los vehículos eléctricos y convencionales seleccionados.  
                **Objetivo del KPI**  
                Este KPI permite a la empresa evaluar la efectividad de sus inversiones, estableciendo una meta de superar el 8% de rentabilidad anual.  
                Con este indicador, la empresa puede identificar áreas de oportunidad para maximizar el retorno, optimizar la asignación de recursos y asegurar 
                que las estrategias de inversión estén alineadas con el crecimiento financiero y la sostenibilidad de la organización""")

with col2:
    st.plotly_chart(kpi_roi_anual(), use_container_width=True)



# KPI: Proporción por cantidad de autos
col3, col4 = st.columns([1, 1], vertical_alignment = 'center')
with col3:
    st.plotly_chart(kpi_proporcion_autos(), use_container_width=True)    
with col4:
    st.markdown("""  
                  
                  
                
                **Proporción de Mercado (Autos)**: Este KPI refleja el porcentaje del mercado que cubre la empresa en función de la cantidad de autos disponibles.  
                **Objetivo del KPI**  
                La meta de la empresa es alcanzar una participación de mercado del 1% mensual en términos de flota operativa en el mercado global de vehículos. 
                Este KPI permitirá evaluar el progreso mensual en la competitividad, 
                midiendo de forma continua cómo contribuyen las diferentes estrategias de crecimiento y expansión.""")


# KPI: Proporción por cantidad de viajes
col5, col6 = st.columns([1, 1],  vertical_alignment = 'center')
with col5:
    st.markdown(  
          
            
            """**Proporción de Mercado (Viajes)**: Este indicador mide la participación de mercado según la cantidad de viajes realizados.  
            **Objetivo del KPI**:  
                Se quiere lograr una participación del 1% en la cantidad de viajes realizados mensualmente en el mercado global de transporte. 
                Este KPI permitirá medir la competitividad de la empresa en términos de actividad operativa, 
                evaluando de forma continua el impacto de nuestras estrategias de crecimiento en el volumen de viajes realizados y en nuestra expansión dentro del mercado.
                """)
with col6:
    st.plotly_chart(kpi_proporcion_viajes(), use_container_width=True)

# KPI: Ahorro de CO2
col7, col8 = st.columns([1, 1], vertical_alignment = 'center')
with col7:
    st.plotly_chart(kpi_ahorro_CO2(), use_container_width=True)
with col8:
        st.markdown(  
              
                
                """**Ahorro de CO2**: Esta proporción se calcula comparando la cantidad de carbono emitido por milla en el mes 
                usando el mix de vehículos REAL (incluyendo convencionales y eléctricos) 
                con la cantidad de carbono que se emitiría si toda la flota fuera de vehículos convencionales.  
                **Objetivo del KPI**:  
                El objetivo es lograr una reducción del 30% en las emisiones de carbono en comparación con una flota totalmente convencional.
                """)

# Interfaz de Streamlit
#st.subheader("Indicadores Clave de Desempeño (KPIs)")
#st.write("Este tablero muestra los KPIs calculados en funcion de los objetivos y la flota elegida de vehículos eléctricos y convencionales.")




# Generar y mostrar el gráfico
#fig = create_kpi_dashboard()
#st.plotly_chart(fig, use_container_width=True)

# Mostrar la imagen cargada
st.image("Images/Piest.png", use_container_width=True)