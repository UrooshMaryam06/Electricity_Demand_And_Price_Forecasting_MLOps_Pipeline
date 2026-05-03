"""
Classification page: classify demand and price level from a feature vector.
Shows the standalone classifier output (NOT regression → threshold conversion).
"""
import streamlit as st
st.set_page_config(page_title="Classification", layout="wide")

with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

from components.sidebar import render_sidebar
from services.api_client import classify_demand, classify_price
from utils.config import COLORS

render_sidebar()
st.markdown("## Classification — Demand & Price Regimes")
st.caption("Classifies current energy conditions into LOW / MED / HIGH categories.")
st.divider()

# ── Feature inputs ────────────────────────────────────────────────────────────
with st.expander("Input Features", expanded=True):
    c1, c2, c3 = st.columns(3)
    with c1:
        hour    = st.slider("Hour", 0, 23, st.session_state.get("selected_hour", 12))
        month   = st.slider("Month", 1, 12, 6)
        weekend = st.checkbox("Weekend")
    with c2:
        solar   = st.number_input("Solar (MW)",    0.0, 10000.0, 3000.0)
        wind    = st.number_input("Wind (MW)",     0.0, 20000.0, 8000.0)
        gas     = st.number_input("Gas (MW)",      0.0, 15000.0, 5000.0)
    with c3:
        demand_lag_1h  = st.number_input("Lag demand 1h", 0.0, 50000.0, 28000.0)
        demand_lag_24h = st.number_input("Lag demand 24h",0.0, 50000.0, 27500.0)
        demand_lag_168h = st.number_input("Lag demand 168h",0.0,50000.0,27000.0)
        price_lag_1h = st.number_input("Price lag 1h (EUR/MWh)", 0.0, 1000.0, 50.0)
        price_lag_24h = st.number_input("Price lag 24h (EUR/MWh)",0.0,1000.0,48.0)
        nuclear = st.number_input("Nuclear (MW)",  0.0, 10000.0, 7000.0)

renewable = solar + wind
fossil = gas
total_gen = renewable + fossil + nuclear if (renewable + fossil + nuclear) != 0 else 0.0
renewable_pct = (renewable / total_gen * 100.0) if total_gen != 0 else 0.0

features = {
    "hour": hour,
    "month": month,
    "is_weekend": int(weekend),
    "generation solar": solar,
    "generation wind onshore": wind,
    "generation nuclear": nuclear,
    "generation fossil gas": gas,
    "renewable": renewable,
    "fossil": fossil,
    "nuclear": nuclear,
    "renewable_pct": renewable_pct,
    "demand_lag_1h": demand_lag_1h,
    "demand_lag_24h": demand_lag_24h,
    "demand_lag_168h": demand_lag_168h,
    "price_lag_1h": price_lag_1h,
    "price_lag_24h": price_lag_24h,
}

if st.button("Classify"):
    d_result = classify_demand(features)
    p_result = classify_price(features)

    if d_result and p_result:
        st.divider()
        col1, col2 = st.columns(2)

        d_class = d_result.get("demand_class", "N/A")
        p_class = p_result.get("price_class",  "N/A")

        label_color = {
            "LOW":  COLORS["low_color"],
            "MED":  COLORS["med_color"],
            "HIGH": COLORS["high_color"],
            "N/A":  COLORS["text_secondary"],
        }

        with col1:
            color = label_color.get(d_class, COLORS["text_secondary"])
            st.markdown(
                f"<div style='background:#1e2130;border:1px solid {color};"
                f"border-radius:6px;padding:24px;text-align:center'>"
                f"<div style='color:#8b91a8;font-size:11px;font-family:IBM Plex Mono;"
                f"text-transform:uppercase;letter-spacing:.08em'>Demand Level</div>"
                f"<div style='color:{color};font-size:40px;font-family:IBM Plex Mono;"
                f"font-weight:600;margin-top:8px'>{d_class}</div></div>",
                unsafe_allow_html=True,
            )
        with col2:
            color = label_color.get(p_class, COLORS["text_secondary"])
            st.markdown(
                f"<div style='background:#1e2130;border:1px solid {color};"
                f"border-radius:6px;padding:24px;text-align:center'>"
                f"<div style='color:#8b91a8;font-size:11px;font-family:IBM Plex Mono;"
                f"text-transform:uppercase;letter-spacing:.08em'>Price Level</div>"
                f"<div style='color:{color};font-size:40px;font-family:IBM Plex Mono;"
                f"font-weight:600;margin-top:8px'>{p_class}</div></div>",
                unsafe_allow_html=True,
            )
