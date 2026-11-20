import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression

# Configuración de la página
st.set_page_config(
    page_title="Dashboard Comercial",
    page_icon="📊",
    layout="wide"
)

# Título
st.title("📊 Dashboard Comercial")
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
# Si el usuario elige solo una fecha, se usa como inicio y fin (evita error)
if isinstance(rango_fechas, (tuple, list)):
    if len(rango_fechas) == 2:
        fecha_ini, fecha_fin = rango_fechas
    else:
        fecha_ini = fecha_fin = rango_fechas[0]
else:
    fecha_ini = fecha_fin = rango_fechas

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
    (df["Fecha"] >= pd.to_datetime(fecha_ini)) &
    (df["Fecha"] <= pd.to_datetime(fecha_fin)) &
    (df["Region"].isin(regiones)) &
    (df["Categoria"].isin(categorias))
]

if df_filtrado.empty:
    st.warning("No hay datos con los filtros seleccionados.")
    st.stop()

# KPIs
st.subheader("📈 Indicadores Clave")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Ventas Totales", f"S/ {df_filtrado['Total'].sum():,.0f}")

with col2:
    st.metric("Cantidad Vendida", f"{df_filtrado['Cantidad'].sum():,}")

with col3:
    st.metric("Ticket Promedio", f"S/ {df_filtrado['Total'].mean():,.0f}")

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

# Ventas por producto y participación por vendedor
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Ventas por Producto")
    top_productos = (
        df_filtrado.groupby("Producto")["Total"].sum()
        .sort_values(ascending=False).reset_index()
    )
    fig4 = px.bar(top_productos, x="Producto", y="Total", color="Total", text_auto=".2s")
    st.plotly_chart(fig4, use_container_width=True)

with col_b:
    st.subheader("Participación por Vendedor")
    ventas_vend = df_filtrado.groupby("Vendedor")["Total"].sum().reset_index()
    fig5 = px.pie(ventas_vend, values="Total", names="Vendedor")
    st.plotly_chart(fig5, use_container_width=True)

# Ventas a lo largo del tiempo
st.subheader("Evolución de Ventas")
ventas_tiempo = df_filtrado.groupby("Fecha")["Total"].sum().reset_index()
fig3 = px.line(ventas_tiempo, x="Fecha", y="Total", markers=True)
st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")

# Predicción IA
st.subheader("🤖 Predicción IA – Crecimiento esperado")
mensual = (
    df_filtrado.groupby(df_filtrado["Fecha"].dt.to_period("M"))["Total"]
    .sum().reset_index()
)
mensual["Mes"] = mensual["Fecha"].dt.to_timestamp()
mensual["n"] = range(len(mensual))

if len(mensual) < 3:
    st.info("Se necesitan al menos 3 meses de datos para generar la predicción. "
            "Amplía el rango de fechas.")
else:
    modelo = LinearRegression().fit(mensual[["n"]], mensual["Total"])
    meses_futuros = 3
    n_futuro = np.arange(len(mensual), len(mensual) + meses_futuros).reshape(-1, 1)
    pred = np.maximum(modelo.predict(n_futuro), 0)
    fechas_futuras = pd.date_range(
        mensual["Mes"].iloc[-1] + pd.offsets.MonthBegin(1),
        periods=meses_futuros, freq="MS"
    )

    ultimo_real = mensual["Total"].iloc[-1]
    crecimiento = (pred[0] - ultimo_real) / ultimo_real * 100 if ultimo_real else 0

    c1, c2 = st.columns(2)
    with c1:
        st.metric("Próximo mes (estimado)", f"S/ {pred[0]:,.0f}",
                  delta=f"{crecimiento:+.1f}% vs último mes")
    with c2:
        tendencia = "al alza 📈" if modelo.coef_[0] > 0 else "a la baja 📉"
        st.metric("Tendencia mensual", f"S/ {modelo.coef_[0]:+,.0f} por mes",
                  delta=tendencia, delta_color="off")

    fig6 = go.Figure()
    fig6.add_trace(go.Scatter(x=mensual["Mes"], y=mensual["Total"],
                              mode="lines+markers", name="Ventas reales"))
    fig6.add_trace(go.Scatter(x=fechas_futuras, y=pred, mode="lines+markers",
                              name="Predicción", line=dict(dash="dash")))
    fig6.update_layout(xaxis_title="Mes", yaxis_title="Ventas (S/)")
    st.plotly_chart(fig6, use_container_width=True)
    st.caption("Modelo: regresión lineal sobre las ventas mensuales. "
               "Con pocos meses de datos es una estimación referencial.")

# Tabla de datos
st.subheader("📋 Datos Detallados")
st.dataframe(df_filtrado, use_container_width=True)
