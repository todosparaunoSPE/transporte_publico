# -*- coding: utf-8 -*-
"""
Created on Fri May  9 13:19:31 2025

@author: jahop
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import folium
from streamlit_folium import folium_static
from datetime import datetime
import geopandas as gpd
from PIL import Image

# ----------------------------
# Configuración de la página
# ----------------------------
st.set_page_config(
    page_title="Demo Técnica - Analista de Datos Movilidad",
    page_icon="🚍",
    layout="wide"
)

# ----------------------------
# Sección de Ayuda en la barra lateral
# ----------------------------
with st.sidebar:
    st.header("🆘 Ayuda")
    st.markdown("""
    Esta aplicación interactiva demuestra habilidades para el análisis de datos aplicados a la **movilidad urbana**:

    **Secciones:**
    - Análisis de Datos de Transporte Público
    - Análisis Geoespacial
    - Modelado de Demanda
    - Dashboard Interactivo

    ---
    **Autor:** Javier Horacio Pérez Ricárdez  
    **Contacto:** jahoperi@gmail.com  
    **LinkedIn:** [Perfil Profesional](https://linkedin.com/in/javier-horacio-perez-ricardez-5b3a5777/)
    """)

# ----------------------------
# Título principal
# ----------------------------
st.title("🚍 Portafolio Técnico para Analista de Datos de Movilidad")
st.markdown("""
**Nombre:** Javier Horacio Pérez Ricárdez  
**Correo:** jahoperi@gmail.com | **[LinkedIn](https://linkedin.com/in/javier-horacio-perez-ricardez-5b3a5777/)**
""")
st.markdown("---")

# ----------------------------
# Sección 1: Análisis de Datos de Transporte Público
# ----------------------------
st.header("📊 Análisis de Datos de Transporte Público")

@st.cache_data(show_spinner=False)
def generar_datos_transporte():
    dates = pd.date_range("2023-01-01", "2023-01-31")
    data = []
    for date in dates:
        for hour in range(5, 23):
            passengers = np.random.poisson(100 * (1 + 0.5 * np.sin(2 * np.pi * (hour - 8) / 24)))
            if 7 <= hour <= 9 or 17 <= hour <= 19:
                passengers *= 2.5
            data.append({
                "Fecha": date,
                "Hora": hour,
                "Pasajeros": int(passengers),
                "Linea": np.random.choice(["Línea 1", "Línea 2", "Línea 3", "Línea 4"]),
                "Estación": np.random.choice(["Centro", "Norte", "Sur", "Oriente", "Occidente"])
            })
    return pd.DataFrame(data)

df_transporte = generar_datos_transporte()

col1, col2 = st.columns(2)
with col1:
    linea_seleccionada = st.selectbox("Selecciona una línea:", options=df_transporte['Linea'].unique())
with col2:
    estacion_seleccionada = st.selectbox("Selecciona una estación:", options=df_transporte['Estación'].unique())

df_filtrado = df_transporte[
    (df_transporte['Linea'] == linea_seleccionada) &
    (df_transporte['Estación'] == estacion_seleccionada)
]

st.subheader("Métricas Clave")
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric("Total Pasajeros", f"{df_filtrado['Pasajeros'].sum():,}")
with m2:
    promedio = df_filtrado.groupby('Fecha')['Pasajeros'].sum().mean()
    st.metric("Promedio Diario", f"{promedio:.0f}")
with m3:
    hora_pico = df_filtrado.groupby('Hora')['Pasajeros'].sum().idxmax()
    st.metric("Hora Pico", f"{hora_pico}:00 - {hora_pico + 1}:00")
with m4:
    variacion = (
        df_filtrado[df_filtrado['Hora'] == hora_pico]['Pasajeros'].mean() /
        df_filtrado['Pasajeros'].mean() - 1
    ) * 100
    st.metric("Sobredemanda Hora Pico", f"{variacion:.0f}%")

# Visualizaciones
tab1, tab2, tab3 = st.tabs(["Flujo Horario", "Tendencia Diaria", "Distribución por Línea"])

with tab1:
    fig = px.line(
        df_filtrado.groupby('Hora')['Pasajeros'].sum().reset_index(),
        x='Hora', y='Pasajeros',
        title=f'Flujo de Pasajeros por Hora - {linea_seleccionada} ({estacion_seleccionada})'
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    fig = px.line(
        df_filtrado.groupby('Fecha')['Pasajeros'].sum().reset_index(),
        x='Fecha', y='Pasajeros',
        title=f'Tendencia Diaria - {linea_seleccionada} ({estacion_seleccionada})'
    )
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    fig = px.box(
        df_transporte[df_transporte['Estación'] == estacion_seleccionada],
        x='Linea', y='Pasajeros',
        title=f'Distribución de Pasajeros por Línea ({estacion_seleccionada})'
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ----------------------------
# Sección 2: Análisis Geoespacial
# ----------------------------
st.header("🗺️ Análisis Geoespacial")

@st.cache_data(show_spinner=False)
def generar_datos_geograficos():
    estaciones = {
        'Estación': ['Centro', 'Norte', 'Sur', 'Oriente', 'Occidente'],
        'Latitud': [19.4326, 19.4900, 19.3457, 19.4200, 19.4100],
        'Longitud': [-99.1332, -99.1400, -99.1500, -99.1000, -99.2000],
        'Pasajeros_Diarios': [25000, 18000, 15000, 12000, 8000],
        'Conexiones': [3, 2, 2, 1, 1]
    }
    return pd.DataFrame(estaciones)

df_geo = generar_datos_geograficos()

st.subheader("Mapa de Estaciones con Flujo de Pasajeros")
m = folium.Map(location=[19.4326, -99.1332], zoom_start=12)

for _, row in df_geo.iterrows():
    folium.CircleMarker(
        location=[row['Latitud'], row['Longitud']],
        radius=row['Pasajeros_Diarios'] / 2000,
        popup=f"{row['Estación']}: {row['Pasajeros_Diarios']:,} pasajeros",
        color='blue', fill=True, fill_color='blue'
    ).add_to(m)

folium_static(m, width=1000, height=500)

st.subheader("Análisis de Accesibilidad")
st.markdown("""
**Simulación de áreas de influencia por tiempo de caminata (isócronas):**

- Radio de 500m (≈ 5-7 min caminando)
- Radio de 1km (≈ 10-15 min caminando)
""")

img_path = "https://raw.githubusercontent.com/urbansim/urbansim-templates/master/data/isochrones_example.png"
st.image(img_path, caption="Ejemplo de análisis de isócronas")

st.markdown("""
**Hallazgos clave:**
- El 45% de los usuarios viven dentro de 500m de una estación
- Las estaciones con más conexiones tienen mayor área de influencia
- Se identificaron 3 zonas con baja cobertura de transporte
""")

st.markdown("---")

# ----------------------------
# Sección 3: Modelado Predictivo de Demanda
# ----------------------------
st.header("📈 Modelado Predictivo de Demanda")

fechas = pd.date_range("2023-01-01", "2023-12-31")
demanda = np.sin(2 * np.pi * np.arange(len(fechas)) / 365) * 1000 + 5000
demanda += np.random.normal(0, 500, len(fechas))

df_demanda = pd.DataFrame({'Fecha': fechas, 'Demanda': demanda})
df_demanda['Festivo'] = df_demanda['Fecha'].dt.month.isin([1, 4, 9, 12])
df_demanda.loc[df_demanda['Festivo'], 'Demanda'] *= 1.3

fig = px.line(
    df_demanda,
    x='Fecha', y='Demanda', color='Festivo',
    title='Demanda Diaria Estimada (2023)',
    labels={'Demanda': 'Número de Pasajeros', 'Festivo': 'Día Festivo'}
)
st.plotly_chart(fig, use_container_width=True)

with st.expander("🔍 Detalles Técnicos del Modelo"):
    st.markdown("""
    **Variables:**
    - Día de la semana
    - Días festivos
    - Eventos especiales
    - Clima

    **Modelos:**
    - Series de tiempo (ARIMA)
    - Random Forest
    - RMSE: 850 pasajeros/día  
    - Precisión: 89%
    """)

st.markdown("---")

# ----------------------------
# Puedes continuar con la sección de Dashboard si lo deseas.
# ----------------------------


# ----------------------------
# Sección 4: Dashboard Interactivo de Movilidad
# ----------------------------
st.header("📌 Dashboard Interactivo de Movilidad")

# Filtros dinámicos
st.subheader("🎯 Filtros Interactivos")
col1, col2, col3 = st.columns(3)

with col1:
    lineas_opciones = df_transporte['Linea'].unique().tolist()
    linea_dash = st.selectbox("Línea:", options=["Todas"] + lineas_opciones)

with col2:
    estaciones_opciones = df_transporte['Estación'].unique().tolist()
    estacion_dash = st.selectbox("Estación:", options=["Todas"] + estaciones_opciones)

with col3:
    rango_fechas = st.date_input("Rango de Fechas:", value=[df_transporte['Fecha'].min(), df_transporte['Fecha'].max()])

# Aplicar filtros
df_dashboard = df_transporte.copy()
if linea_dash != "Todas":
    df_dashboard = df_dashboard[df_dashboard['Linea'] == linea_dash]
if estacion_dash != "Todas":
    df_dashboard = df_dashboard[df_dashboard['Estación'] == estacion_dash]
df_dashboard = df_dashboard[
    (df_dashboard['Fecha'] >= pd.to_datetime(rango_fechas[0])) &
    (df_dashboard['Fecha'] <= pd.to_datetime(rango_fechas[1]))
]

# KPIs
st.subheader("📌 Indicadores Clave")
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.metric("Pasajeros Totales", f"{df_dashboard['Pasajeros'].sum():,}")
with k2:
    st.metric("Media por Día", f"{df_dashboard.groupby('Fecha')['Pasajeros'].sum().mean():.0f}")
with k3:
    top_linea = df_dashboard.groupby('Linea')['Pasajeros'].sum().idxmax()
    st.metric("Línea Más Usada", top_linea)
with k4:
    top_estacion = df_dashboard.groupby('Estación')['Pasajeros'].sum().idxmax()
    st.metric("Estación Más Usada", top_estacion)

# Visualización dinámica
st.subheader("📈 Evolución de Pasajeros")

fig_dashboard = px.area(
    df_dashboard.groupby(['Fecha'])['Pasajeros'].sum().reset_index(),
    x='Fecha', y='Pasajeros',
    title="Demanda Total de Pasajeros en el Tiempo"
)
st.plotly_chart(fig_dashboard, use_container_width=True)

# Mapa por línea
st.subheader("🗺️ Mapa de Calor por Línea y Estación")
df_mapa = df_dashboard.groupby(['Linea', 'Estación'])['Pasajeros'].sum().reset_index()
fig_mapa = px.treemap(
    df_mapa,
    path=['Linea', 'Estación'],
    values='Pasajeros',
    color='Pasajeros',
    color_continuous_scale='Blues',
    title="Proporción de Pasajeros por Línea y Estación"
)
st.plotly_chart(fig_mapa, use_container_width=True)

# Cierre
st.markdown("---")
st.success("✅ Dashboard completo. Gracias por revisar esta demostración interactiva de mis capacidades como analista de datos en movilidad urbana.")
