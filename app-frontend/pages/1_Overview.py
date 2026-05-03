"""
System overview: KPIs, best model, recent pipeline status.
This is the "executive view" — one page that shows if everything is working.
"""
import streamlit as st
st.set_page_config(page_title="Overview", layout="wide")

with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

from components.sidebar import render_sidebar
from components.kpi_cards import render_kpi_row
from services.api_client import get_health, get_model_comparison, get_recommendation
from components.charts import model_comparison_bar

render_sidebar()
st.markdown("## System Overview")
st.divider()

# ── Row 1: API health KPIs ────────────────────────────────────────────────────
health = get_health()
if health:
    render_kpi_row([
        {"label": "API Status",     "value": "Online"},
        {"label": "Version",        "value": health.get("version", "1.0")},
        {"label": "Models Loaded",  "value": str(health.get("models_loaded", 0))},
        {"label": "Uptime",         "value": health.get("uptime", "N/A")},
    ])
else:
    st.error("API is offline. Start FastAPI before using this dashboard.")

st.divider()

# ── Row 2: Best model ─────────────────────────────────────────────────────────
rec = get_recommendation()
if rec:
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("**Recommended Model**")
        st.metric("Best Model",   rec.get("best_model", "N/A"))
        st.metric("Best Avg R2",  f"{rec.get('best_score', 0):.4f}")
    with col2:
        st.markdown("**Reasoning**")
        st.info(rec.get("reason", "Model selected by highest average R2 across demand and price."))

st.divider()

# ── Row 3: Model comparison bar chart ────────────────────────────────────────
comparison = get_model_comparison()
if comparison:
    st.markdown("**Model Performance Summary**")
    # Parse the comparison response — adjust field names to match your API response
    models = list(comparison.keys())
    rmse_d = [comparison[m].get("demand_rmse", 0) for m in models]
    r2_d   = [comparison[m].get("demand_r2",   0) for m in models]
    fig = model_comparison_bar(models, rmse_d, r2_d, "Demand Forecasting — All Models")
    st.plotly_chart(fig, use_container_width=True)
