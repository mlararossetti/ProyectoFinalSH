#pagina de dashboards
import streamlit as st

# Título de la aplicación
st.title("Dashboards interactivos")

st.markdown(
    """
    ####  Dashboard 1: Análisis Temporal y por Industria del Mercado
   """
)
st.markdown("[Ir al Dashboard N°1](./pagina3)")

st.markdown(
    """
    ####  Dashboard 2:  Análisis Georreferencial de Viajes
   """
)
st.markdown("[Ir al Dashboard N°2](./pagina4)")

st.markdown(
    """
    ####  Dashboard 3: Análisis Impacto Ambiental
   """
)

# Crear un enlace a otra página
st.markdown("[Ir al Dashboard N°3](./pagina5)")


st.markdown(
    """
    ####  Dashboard 4: Análisis Financiero de Vehículos Eléctricos
 
Contiene una primera instancia de evaluación financiera personalizada. 
Esta sección dinámica del dashboard permite analizar de manera específica los indicadores financieros clave 
(ROI Total, ROI Anual, TIR y Payback Period) 
para cualquier modelo de vehículo eléctrico seleccionado. Esto facilita a los usuarios evaluar la viabilidad económica de una inversión en función de sus necesidades o preferencias.

Luego nos muestra el cumplimiento de KPI, donde la herramienta destaca si un vehículo cumple con el KPI establecido de un ROI anual mínimo del 8%. Este enfoque orientado al desempeño ayuda a filtrar opciones y priorizar inversiones que sean financieramente sostenibles.

Por último un apartado de análisis comparativo de las mejores opciones. En esta  sección estática, se presentan los Top 5 vehículos eléctricos en varias categorías clave:
- Costo más bajo: Identifica los vehículos más asequibles, útil para quienes buscan opciones económicas.
- Mayor eficiencia energética: Destaca los modelos con menor consumo de energía por kilómetro, ideal para usuarios enfocados en ahorro energético.
- Mejor relación precio/eficiencia: Proporciona un balance óptimo entre costo y rendimiento energético.
- Mejor ROI Anual: Prioriza las opciones con los mayores retornos financieros anuales.
"""
)

# URL del dashboard de Power BI
power_bi_url = "https://app.powerbi.com/view?r=eyJrIjoiMjQwY2FjZjAtZmVjNC00N2NlLTg1MmQtNjI2Njg1M2RiNDJlIiwidCI6IjkyZTI3Mzg0LWI2YjAtNGIxMy05ZWU4LTFkOGY2ZGI5YzdmNSJ9"

# Inserta el iframe como HTML
iframe_html = f"""
<iframe
    src="{power_bi_url}"
    width="1000"
    height="800"
    frameborder="0"
    allowFullScreen="true">
</iframe>
"""
st.markdown(iframe_html, unsafe_allow_html=True)

# Mostrar la imagen cargada
st.image("Images/Piest.png", use_container_width=True)