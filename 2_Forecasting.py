"""
Forecasting page: build a feature vector from sliders, call /predict/both,
display 12-step ahead forecast from the historical dataset.
"""
import datetime
from pathlib import Path

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
st.set_page_config(page_title="Forecasting", layout="wide")

with open(Path(__file__).resolve().parents[1] / "assets" / "style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

from components.sidebar import render_sidebar
from services.api_client import predict_both
from services.data_loader import load_dataset
from utils.config import COLORS

render_sidebar()
st.markdown("## Demand & Price Forecasting")
st.divider()

df = load_dataset()

# ── INPUT SECTION (replaced) ──────────────────────────────────────────────────
from components.raw_input_form import render_raw_input_form
from services.feature_engineering import build_all_features

st.markdown("### Input Features")
with st.expander("Input Features", expanded=True):
    raw = render_raw_input_form(key_prefix="forecast_")

_built          = build_all_features(raw)
demand_features = _built['demand_features']   # 19 features → demand model
price_features  = _built['price_features']    # 19 features → price model
gen_breakdown   = _built['generation_breakdown']

# Show computed generation mix
_gc1, _gc2, _gc3, _gc4, _gc5 = st.columns(5)
_gc1.metric("Renewable",   f"{gen_breakdown['Renewable']:,.0f} MW")
_gc2.metric("Fossil",      f"{gen_breakdown['Fossil']:,.0f} MW")
_gc3.metric("Nuclear",     f"{gen_breakdown['Nuclear']:,.0f} MW")
_gc4.metric("Other",       f"{gen_breakdown['Other']:,.0f} MW")
_gc5.metric("Renewable %", f"{gen_breakdown['Renewable %']:.1f}%")
# ── END INPUT SECTION ─────────────────────────────────────────────────────────

if st.button("Run Prediction"):
    result = predict_both(demand_features)
    if result:
        st.divider()
        c1, c2 = st.columns(2)
        c1.metric("Predicted Demand", f"{result.get('predicted_demand_12h_MW', 0):,.0f} MW")
        c2.metric("Predicted Price",  f"€{result.get('predicted_price_12h_EUR', 0):.2f} / MWh")

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
