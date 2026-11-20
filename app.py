import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression

# ---------------------------------------------------------------- Configuración
st.set_page_config(
    page_title="Dashboard Comercial",
    page_icon="📊",
    layout="wide"
)

# Paleta de colores
AZUL_OSCURO = "#0B2E59"
AZUL = "#1F6FEB"
TURQUESA = "#14B8A6"
AMBAR = "#F59E0B"
MORADO = "#8B5CF6"
ROJO = "#EF4444"
PALETA = [AZUL, TURQUESA, AMBAR, MORADO, ROJO, "#64748B"]

# ---------------------------------------------------------------- Estilos (CSS)
st.markdown("""
<style>
.block-container {padding-top: 1.5rem; padding-bottom: 2rem; max-width: 1300px;}
#MainMenu, footer {visibility: hidden;}

/* Banner superior */
.banner {
    background: linear-gradient(120deg, #0B2E59 0%, #1F6FEB 100%);
    color: white; padding: 26px 32px; border-radius: 16px; margin-bottom: 22px;
    box-shadow: 0 6px 18px rgba(31,111,235,0.25);
}
.banner h1 {margin: 0; font-size: 2rem; color: white; font-weight: 700;}
.banner p {margin: 6px 0 0 0; opacity: 0.85; font-size: 0.95rem; color: white;}

/* Tarjetas de indicadores */
.kpi {
    background: white; border-radius: 14px; padding: 18px 20px;
    box-shadow: 0 2px 10px rgba(11,46,89,0.08); border-left: 6px solid #1F6FEB;
    height: 100%;
}
.kpi .label {font-size: 0.82rem; color: #64748B; text-transform: uppercase;
             letter-spacing: 0.04em; font-weight: 600;}
.kpi .value {font-size: 1.9rem; font-weight: 700; color: #0B2E59; margin-top: 4px;}
.kpi .sub {font-size: 0.8rem; color: #64748B; margin-top: 2px;}

/* Títulos de sección */
.seccion {font-size: 1.25rem; font-weight: 700; color: #0B2E59;
          margin: 26px 0 10px 0; padding-left: 12px; border-left: 5px solid #14B8A6;}

/* Contenedores de gráficos como tarjetas */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: white; border-radius: 14px; border: none !important;
    box-shadow: 0 2px 10px rgba(11,46,89,0.08);
}
.grafico-titulo {font-size: 1rem; font-weight: 600; color: #0B2E59; margin-bottom: 2px;}

/* Barra lateral */
section[data-testid="stSidebar"] {background: #FFFFFF; border-right: 1px solid #E2E8F0;}
section[data-testid="stSidebar"] h2 {color: #0B2E59;}
</style>
""", unsafe_allow_html=True)


def tarjeta(label, valor, sub="", color=AZUL):
    st.markdown(
        f"""<div class="kpi" style="border-left-color:{color}">
            <div class="label">{label}</div>
            <div class="value">{valor}</div>
            <div class="sub">{sub}</div></div>""",
        unsafe_allow_html=True
    )


def seccion(texto):
    st.markdown(f'<div class="seccion">{texto}</div>', unsafe_allow_html=True)


def estilo_grafico(fig, moneda=True):
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=10, b=10),
        font=dict(family="Arial", color=AZUL_OSCURO),
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
    )
    if moneda:
        fig.update_yaxes(tickprefix="S/ ", gridcolor="#E2E8F0")
    return fig


# ---------------------------------------------------------------- Datos
@st.cache_data
def cargar_datos():
    df = pd.read_csv("ventas.csv")
    df["Fecha"] = pd.to_datetime(df["Fecha"])
    df["Total"] = df["Cantidad"] * df["Precio"]
    return df


df = cargar_datos()

# ---------------------------------------------------------------- Filtros
st.sidebar.header("🔍 Filtros")

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

regiones = st.sidebar.multiselect(
    "Región", options=df["Region"].unique(), default=df["Region"].unique()
)
categorias = st.sidebar.multiselect(
    "Categoría", options=df["Categoria"].unique(), default=df["Categoria"].unique()
)

df_filtrado = df[
    (df["Fecha"] >= pd.to_datetime(fecha_ini)) &
    (df["Fecha"] <= pd.to_datetime(fecha_fin)) &
    (df["Region"].isin(regiones)) &
    (df["Categoria"].isin(categorias))
]

# ---------------------------------------------------------------- Banner
st.markdown(
    f"""<div class="banner">
        <h1>📊 Dashboard Comercial</h1>
        <p>Resumen de ventas · {pd.to_datetime(fecha_ini):%d/%m/%Y} al
        {pd.to_datetime(fecha_fin):%d/%m/%Y} · {len(df_filtrado)} registros</p>
    </div>""",
    unsafe_allow_html=True
)

if df_filtrado.empty:
    st.warning("No hay datos con los filtros seleccionados.")
    st.stop()

# ---------------------------------------------------------------- KPIs
k1, k2, k3, k4 = st.columns(4)
with k1:
    tarjeta("Ventas Totales", f"S/ {df_filtrado['Total'].sum():,.0f}",
            "Suma de todas las ventas", AZUL)
with k2:
    tarjeta("Cantidad Vendida", f"{df_filtrado['Cantidad'].sum():,}",
            "Unidades", TURQUESA)
with k3:
    tarjeta("Ticket Promedio", f"S/ {df_filtrado['Total'].mean():,.0f}",
            "Promedio por venta", AMBAR)
with k4:
    tarjeta("Productos Únicos", df_filtrado["Producto"].nunique(),
            "Productos distintos", MORADO)

# ---------------------------------------------------------------- Gráficos
seccion("Ventas por producto y vendedor")
col_a, col_b = st.columns(2)

with col_a:
    with st.container(border=True):
        st.markdown('<div class="grafico-titulo">Ventas por Producto</div>',
                    unsafe_allow_html=True)
        top_productos = (df_filtrado.groupby("Producto")["Total"].sum()
                         .sort_values(ascending=False).reset_index())
        fig4 = px.bar(top_productos, x="Producto", y="Total", text_auto=".2s",
                      color_discrete_sequence=[AZUL])
        fig4.update_traces(marker_cornerradius=6)
        st.plotly_chart(estilo_grafico(fig4), width="stretch")

with col_b:
    with st.container(border=True):
        st.markdown('<div class="grafico-titulo">Participación por Vendedor</div>',
                    unsafe_allow_html=True)
        ventas_vend = df_filtrado.groupby("Vendedor")["Total"].sum().reset_index()
        fig5 = px.pie(ventas_vend, values="Total", names="Vendedor", hole=0.45,
                      color_discrete_sequence=PALETA)
        fig5.update_traces(textinfo="percent+label")
        st.plotly_chart(estilo_grafico(fig5, moneda=False), width="stretch")

seccion("Ventas por región y categoría")
col_izq, col_der = st.columns(2)

with col_izq:
    with st.container(border=True):
        st.markdown('<div class="grafico-titulo">Ventas por Región</div>',
                    unsafe_allow_html=True)
        ventas_region = df_filtrado.groupby("Region")["Total"].sum().reset_index()
        fig1 = px.bar(ventas_region, x="Region", y="Total", color="Region",
                      text_auto=".2s", color_discrete_sequence=PALETA)
        fig1.update_traces(marker_cornerradius=6)
        fig1.update_layout(showlegend=False)
        st.plotly_chart(estilo_grafico(fig1), width="stretch")

with col_der:
    with st.container(border=True):
        st.markdown('<div class="grafico-titulo">Ventas por Categoría</div>',
                    unsafe_allow_html=True)
        ventas_cat = df_filtrado.groupby("Categoria")["Total"].sum().reset_index()
        fig2 = px.pie(ventas_cat, values="Total", names="Categoria", hole=0.45,
                      color_discrete_sequence=PALETA)
        fig2.update_traces(textinfo="percent+label")
        st.plotly_chart(estilo_grafico(fig2, moneda=False), width="stretch")

seccion("Evolución de ventas")
with st.container(border=True):
    ventas_tiempo = df_filtrado.groupby("Fecha")["Total"].sum().reset_index()
    fig3 = px.line(ventas_tiempo, x="Fecha", y="Total", markers=True,
                   color_discrete_sequence=[TURQUESA])
    fig3.update_traces(line=dict(width=3), marker=dict(size=8))
    st.plotly_chart(estilo_grafico(fig3), width="stretch")

# ---------------------------------------------------------------- Predicción IA
seccion("🤖 Predicción IA – Crecimiento esperado")
mensual = (df_filtrado.groupby(df_filtrado["Fecha"].dt.to_period("M"))["Total"]
           .sum().reset_index())
mensual["Mes"] = mensual["Fecha"].dt.to_timestamp()
mensual["n"] = range(len(mensual))

if len(mensual) < 3:
    st.info("Se necesitan al menos 3 meses de datos para generar la predicción. "
            "Amplía el rango de fechas.")
else:
    modelo = LinearRegression().fit(mensual[["n"]], mensual["Total"])
    meses_futuros = 3
    n_futuro = pd.DataFrame({"n": range(len(mensual), len(mensual) + meses_futuros)})
    pred = np.maximum(modelo.predict(n_futuro), 0)
    fechas_futuras = pd.date_range(
        mensual["Mes"].iloc[-1] + pd.offsets.MonthBegin(1),
        periods=meses_futuros, freq="MS"
    )
    ultimo_real = mensual["Total"].iloc[-1]
    crecimiento = (pred[0] - ultimo_real) / ultimo_real * 100 if ultimo_real else 0
    sube = modelo.coef_[0] > 0
    color_tend = TURQUESA if sube else ROJO
    flecha = "▲" if sube else "▼"

    p1, p2, p3 = st.columns(3)
    with p1:
        tarjeta("Próximo mes (estimado)", f"S/ {pred[0]:,.0f}",
                f"{flecha} {crecimiento:+.1f}% vs último mes", color_tend)
    with p2:
        tarjeta("Tendencia mensual", f"S/ {modelo.coef_[0]:+,.0f}",
                "por mes · " + ("al alza" if sube else "a la baja"), color_tend)
    with p3:
        r2 = modelo.score(mensual[["n"]], mensual["Total"])
        tarjeta("Ajuste del modelo (R²)", f"{r2:.2f}",
                "Más cerca de 1 = mejor ajuste", MORADO)

    with st.container(border=True):
        fig6 = go.Figure()
        fig6.add_trace(go.Scatter(x=mensual["Mes"], y=mensual["Total"],
                                  mode="lines+markers", name="Ventas reales",
                                  line=dict(color=AZUL, width=3)))
        fig6.add_trace(go.Scatter(x=fechas_futuras, y=pred, mode="lines+markers",
                                  name="Predicción",
                                  line=dict(color=AMBAR, width=3, dash="dash")))
        st.plotly_chart(estilo_grafico(fig6), width="stretch")
    st.caption("Modelo: regresión lineal sobre las ventas mensuales. "
               "Con pocos meses de datos es una estimación referencial.")

# ---------------------------------------------------------------- Tabla
seccion("📋 Datos detallados")
with st.container(border=True):
    st.dataframe(df_filtrado, width="stretch", hide_index=True)