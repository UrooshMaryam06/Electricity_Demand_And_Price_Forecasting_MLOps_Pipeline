"""
Classification page: classify demand and price level from a feature vector.
Shows the standalone classifier output (NOT regression → threshold conversion).
"""
from pathlib import Path

import streamlit as st
st.set_page_config(page_title="Classification", layout="wide")

with open(Path(__file__).resolve().parents[1] / "assets" / "style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

from components.sidebar import render_sidebar
from services.api_client import classify_demand, classify_price
from utils.config import COLORS

render_sidebar()
st.markdown("## Classification — Demand & Price Regimes")
st.caption("Classifies current energy conditions into LOW / MED / HIGH categories.")
st.divider()

# ── INPUT SECTION (replaced) ──────────────────────────────────────────────────
from components.raw_input_form import render_raw_input_form
from services.feature_engineering import build_all_features

with st.expander("Input Features", expanded=True):
    raw = render_raw_input_form(key_prefix="classify_")

_built          = build_all_features(raw)
demand_features = _built['demand_features']
price_features  = _built['price_features']
# ── END INPUT SECTION ─────────────────────────────────────────────────────────

if st.button("Classify"):
    d_result = classify_demand(demand_features)
    p_result = classify_price(price_features)

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
