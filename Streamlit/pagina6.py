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

# URL del dashboard de Power BI
power_bi_url = "https://app.powerbi.com/view?r=eyJrIjoiOWI3MWRjODQtYjVlYS00Y2NmLTk3N2MtOTAwZTM3ZTUzNzI5IiwidCI6IjkyZTI3Mzg0LWI2YjAtNGIxMy05ZWU4LTFkOGY2ZGI5YzdmNSJ9"

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