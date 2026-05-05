"""
Model comparison: all 8 trained models benchmarked side by side.
Includes bar chart, radar chart, and metrics table.
"""
import json
from pathlib import Path

import streamlit as st
import pandas as pd
st.set_page_config(page_title="Model Comparison", layout="wide")

with open(Path(__file__).resolve().parents[1] / "assets" / "style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

from components.sidebar import render_sidebar
from services.api_client import get_model_comparison
from components.charts import model_comparison_bar, radar_chart

render_sidebar()
st.markdown("## Model Comparison")
st.divider()

data = get_model_comparison()

if data is None:
    st.warning("Model comparison data unavailable. Ensure API is running.")
    st.stop()

# Parse into a DataFrame — adjust field names to match your API response
rows = []
for model_name, metrics in data.items():
    # Support multiple metric naming conventions from the backend
    def get_metric(keys, default=0.0):
        for k in keys:
            if k in metrics:
                return metrics.get(k)
        return default

    rows.append({
        "Model":        model_name,
        "Demand RMSE":  round(float(get_metric(["demand_rmse", "demand_rmse"], 0.0)), 2),
        "Demand MAE":   round(float(get_metric(["demand_mae", "demand_nmae", "demand_mae"], 0.0)), 2),
        "Demand R2":    round(float(get_metric(["demand_r2", "demand_r2"], 0.0)), 4),
        "Price RMSE":   round(float(get_metric(["price_rmse", "price_rmse"], 0.0)), 2),
        "Price MAE":    round(float(get_metric(["price_mae", "price_nmae", "price_mae"], 0.0)), 2),
        "Price R2":     round(float(get_metric(["price_r2", "price_r2"], 0.0)), 4),
    })

metrics_df = pd.DataFrame(rows).sort_values("Demand R2", ascending=False)

# ── Table ─────────────────────────────────────────────────────────────────────
st.markdown("### Metrics Table")
st.dataframe(
    metrics_df.style.highlight_max(
        subset=["Demand R2", "Price R2"], color="#1e3a2e"
    ).highlight_min(
        subset=["Demand RMSE", "Price RMSE"], color="#1e3a2e"
    ),
    use_container_width=True,
    hide_index=True,
)

# ── Bar chart ─────────────────────────────────────────────────────────────────
st.divider()
tab1, tab2 = st.tabs(["Demand Forecasting", "Price Forecasting"])
with tab1:
    fig = model_comparison_bar(
        metrics_df["Model"].tolist(),
        metrics_df["Demand RMSE"].tolist(),
        metrics_df["Demand R2"].tolist(),
        "Demand Models — RMSE vs R2",
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    fig = model_comparison_bar(
        metrics_df["Model"].tolist(),
        metrics_df["Price RMSE"].tolist(),
        metrics_df["Price R2"].tolist(),
        "Price Models — RMSE vs R2",
    )
    st.plotly_chart(fig, use_container_width=True)

# ── Radar chart ───────────────────────────────────────────────────────────────
st.divider()
st.markdown("### Radar Comparison (normalized scores)")

# Normalize each metric to 0-1 for radar chart
def normalize(series):
    if series.max() == series.min():
        return series * 0
    return (series - series.min()) / (series.max() - series.min())

norm_d_r2   = normalize(metrics_df["Demand R2"]).tolist()
# For RMSE lower is better — invert normalization
norm_d_rmse = (1 - normalize(metrics_df["Demand RMSE"])).tolist()
norm_p_r2   = normalize(metrics_df["Price R2"]).tolist()
norm_p_rmse = (1 - normalize(metrics_df["Price RMSE"])).tolist()

values_matrix = [
    [dr2, drmse, pr2, prmse]
    for dr2, drmse, pr2, prmse
    in zip(norm_d_r2, norm_d_rmse, norm_p_r2, norm_p_rmse)
]

fig = radar_chart(
    model_names=metrics_df["Model"].tolist(),
    metric_names=["Demand R2", "Demand RMSE (inv)", "Price R2", "Price RMSE (inv)"],
    values_matrix=values_matrix,
)
st.plotly_chart(fig, use_container_width=True)

st.divider()
st.markdown("### Experiment Log Summary")
log_path = Path("../artifacts/experiment_log.json")
if log_path.exists():
    try:
        with open(log_path, "r", encoding="utf8") as f:
            exp_log = json.load(f)

        left, right = st.columns(2)
        with left:
            st.markdown("**Best Models**")
            st.write("Demand:", exp_log.get("best_models", {}).get("demand", {}).get("model", "N/A"))
            st.write("Price:", exp_log.get("best_models", {}).get("price", {}).get("model", "N/A"))
        with right:
            st.markdown("**Deployment / Reliability Notes**")
            obs = exp_log.get("observations", {})
            st.write(obs.get("deployment_speed", "N/A"))
            st.write(obs.get("prefect_reliability", "N/A"))

        st.markdown("**Data Quality Issues**")
        st.write(exp_log.get("observations", {}).get("data_quality_issues", []))
        st.markdown("**Overfitting / Underfitting Patterns**")
        st.write(exp_log.get("observations", {}).get("overfitting_patterns", []))
    except Exception as e:
        st.warning(f"Could not read experiment log: {e}")
else:
    st.info("Run the notebook save/log cell first to create artifacts/experiment_log.json.")
