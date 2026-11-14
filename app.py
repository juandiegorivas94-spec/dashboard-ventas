import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(
    page_title="Dashboard de Ventas",
    page_icon="📊",
    layout="wide"
)

# Título
st.title("📊 Dashboard de Ventas")
st.markdown("---")

# Cargar datos
@st.cache_data
def cargar_datos():
    df = pd.read_csv("ventas.csv")
    df["Fecha"] = pd.to_datetime(df["Fecha"])
    df["Total"] = df["Cantidad"] * df["Precio"]
    return df

df = cargar_datos()

# Sidebar - Filtros
st.sidebar.header("🔍 Filtros")

# Filtro por fecha
fecha_min = df["Fecha"].min()
fecha_max = df["Fecha"].max()
rango_fechas = st.sidebar.date_input(
    "Rango de fechas",
    value=(fecha_min, fecha_max),
    min_value=fecha_min,
    max_value=fecha_max
)

# Filtro por región
regiones = st.sidebar.multiselect(
    "Región",
    options=df["Region"].unique(),
    default=df["Region"].unique()
)

# Filtro por categoría
categorias = st.sidebar.multiselect(
    "Categoría",
    options=df["Categoria"].unique(),
    default=df["Categoria"].unique()
)

# Aplicar filtros
df_filtrado = df[
    (df["Fecha"] >= pd.to_datetime(rango_fechas[0])) &
    (df["Fecha"] <= pd.to_datetime(rango_fechas[1])) &
    (df["Region"].isin(regiones)) &
    (df["Categoria"].isin(categorias))
]

# KPIs
st.subheader("📈 Indicadores Clave")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Ventas Totales", f"${df_filtrado['Total'].sum():,.0f}")

with col2:
    st.metric("Cantidad Vendida", f"{df_filtrado['Cantidad'].sum():,}")

with col3:
    st.metric("Ticket Promedio", f"${df_filtrado['Total'].mean():,.0f}")

with col4:
    st.metric("Productos Únicos", df_filtrado["Producto"].nunique())

st.markdown("---")

# Gráficos
col_izq, col_der = st.columns(2)

with col_izq:
    st.subheader("Ventas por Región")
    ventas_region = df_filtrado.groupby("Region")["Total"].sum().reset_index()
    fig1 = px.bar(ventas_region, x="Region", y="Total", color="Region", text_auto=".2s")
    fig1.update_layout(showlegend=False)
    st.plotly_chart(fig1, use_container_width=True)

with col_der:
    st.subheader("Ventas por Categoría")
    ventas_cat = df_filtrado.groupby("Categoria")["Total"].sum().reset_index()
    fig2 = px.pie(ventas_cat, values="Total", names="Categoria", hole=0.4)
    st.plotly_chart(fig2, use_container_width=True)

# Ventas a lo largo del tiempo
st.subheader("Evolución de Ventas")
ventas_tiempo = df_filtrado.groupby("Fecha")["Total"].sum().reset_index()
fig3 = px.line(ventas_tiempo, x="Fecha", y="Total", markers=True)
st.plotly_chart(fig3, use_container_width=True)

# Top productos
st.subheader("Top Productos")
top_productos = df_filtrado.groupby("Producto")["Total"].sum().sort_values(ascending=False).reset_index()
fig4 = px.bar(top_productos, x="Producto", y="Total", color="Total", text_auto=".2s")
st.plotly_chart(fig4, use_container_width=True)

# Tabla de datos
st.subheader("📋 Datos Detallados")
st.dataframe(df_filtrado, use_container_width=True)