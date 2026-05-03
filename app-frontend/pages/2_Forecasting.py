"""
Forecasting page: build a feature vector from sliders, call /predict/both,
display 12-step ahead forecast from the historical dataset.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
st.set_page_config(page_title="Forecasting", layout="wide")

with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

from components.sidebar import render_sidebar
from services.api_client import predict_both
from services.data_loader import load_dataset
from utils.config import COLORS

render_sidebar()
st.markdown("## Demand & Price Forecasting")
st.divider()

df = load_dataset()

# ── Controls ──────────────────────────────────────────────────────────────────
st.markdown("### Input Features")
col1, col2, col3, col4 = st.columns(4)

with col1:
    hour     = st.slider("Hour", 0, 23, st.session_state.get("selected_hour", 12))
    month    = st.slider("Month", 1, 12, 6)
    is_wkend = st.checkbox("Weekend")
with col2:
    solar    = st.number_input("Solar generation (MW)",    0.0, 10000.0, 3000.0, step=100.0)
    wind     = st.number_input("Wind onshore (MW)",        0.0, 20000.0, 8000.0, step=100.0)
    nuclear  = st.number_input("Nuclear (MW)",             0.0, 10000.0, 7000.0, step=100.0)
with col3:
    gas      = st.number_input("Fossil gas (MW)",          0.0, 15000.0, 5000.0, step=100.0)
    coal     = st.number_input("Fossil hard coal (MW)",    0.0, 12000.0, 2000.0, step=100.0)
    hydro    = st.number_input("Hydro water reservoir (MW)",0.0, 8000.0, 2000.0, step=100.0)
with col4:
    demand_lag_1h   = st.number_input("Demand lag 1h (MW)",       0.0, 50000.0, 28000.0, step=100.0)
    demand_lag_24h  = st.number_input("Demand lag 24h (MW)",      0.0, 50000.0, 27500.0, step=100.0)
    demand_lag_168h = st.number_input("Demand lag 168h (MW)",     0.0, 50000.0, 27000.0, step=100.0)
    price_lag_1h    = st.number_input("Price lag 1h (EUR/MWh)",   0.0, 1000.0, 50.0, step=1.0)
    price_lag_24h   = st.number_input("Price lag 24h (EUR/MWh)",  0.0, 1000.0, 48.0, step=1.0)
    load_fc  = st.number_input("Load forecast (MW)",              0.0, 50000.0, 28000.0, step=100.0)

# Build the feature dict that matches FeaturesInput in main.py
# Compute aggregated features expected by the API: renewable, fossil, nuclear, renewable_pct
renewable = solar + wind + hydro
fossil = gas + coal
total_gen = renewable + fossil + nuclear if (renewable + fossil + nuclear) != 0 else 0.0
renewable_pct = (renewable / total_gen * 100.0) if total_gen != 0 else 0.0

features = {
    "hour": hour,
    "month": month,
    "is_weekend": int(is_wkend),
    "generation solar": solar,
    "generation wind onshore": wind,
    "generation nuclear": nuclear,
    "generation fossil gas": gas,
    "generation fossil hard coal": coal,
    "generation hydro water reservoir": hydro,
    "renewable": renewable,
    "fossil": fossil,
    "nuclear": nuclear,
    "renewable_pct": renewable_pct,
    "demand_lag_1h": demand_lag_1h,
    "demand_lag_24h": demand_lag_24h,
    "demand_lag_168h": demand_lag_168h,
    "price_lag_1h": price_lag_1h,
    "price_lag_24h": price_lag_24h,
    "total_load_forecast": load_fc,
}

if st.button("Run Prediction"):
    result = predict_both(features)
    if result:
        st.divider()
        c1, c2 = st.columns(2)
        c1.metric("Predicted Demand", f"{result.get('demand_prediction', 0):,.0f} MW")
        c2.metric("Predicted Price",  f"€{result.get('price_prediction', 0):.2f} / MWh")

# ── Historical actual vs forecast chart ──────────────────────────────────────
if not df.empty:
    st.divider()
    st.markdown("### Historical Series")
    start, end = st.session_state.get("date_range", (df.index.min().date(), df.index.max().date()))
    mask = (df.index.date >= start) & (df.index.date <= end)
    plot_df = df[mask].copy()

    if len(plot_df) > 0:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=plot_df.index, y=plot_df['total load actual'],
            name="Demand (MW)",
            line=dict(color=COLORS["demand_color"], width=1),
        ))
        fig2_ax = fig  # share the figure, use secondary y
        fig.add_trace(go.Scatter(
            x=plot_df.index, y=plot_df['price actual'],
            name="Price (EUR/MWh)",
            line=dict(color=COLORS["price_color"], width=1),
            yaxis="y2",
        ))
        fig.update_layout(
            paper_bgcolor=COLORS["bg_card"], plot_bgcolor=COLORS["bg_card"],
            font=dict(color=COLORS["text_primary"]),
            yaxis=dict(title="Demand (MW)",    gridcolor=COLORS["border"]),
            yaxis2=dict(title="Price (EUR/MWh)", overlaying="y", side="right",
                        gridcolor=COLORS["border"]),
            legend=dict(bgcolor=COLORS["bg_card"]),
            margin=dict(l=40, r=40, t=30, b=40),
        )
        st.plotly_chart(fig, use_container_width=True)
