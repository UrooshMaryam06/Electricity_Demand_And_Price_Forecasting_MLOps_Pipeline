"""Five-tab ML dashboard aligned to project endpoints.

Tabs:
1) Live Prediction
2) 12h Forecast
3) Model Comparison
4) Cluster Explorer
5) Association Rules
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from components.sidebar import render_sidebar
from services.api_client import (
    classify_demand,
    get_cluster_profiles,
    get_model_comparison,
    get_model_registry,
    get_top_associations,
    predict_both,
    query_associations,
)
from utils.config import COLORS


st.set_page_config(page_title="ML Dashboard", layout="wide")

with open("assets/style.css", encoding="utf8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

render_sidebar()
st.title("ML Project Dashboard")
st.caption("Endpoint-aligned dashboard using Streamlit + FastAPI")


def _inputs(prefix: str) -> dict:
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        hour = st.slider("Hour", 0, 23, 12, key=f"{prefix}_hour")
        day_of_week = st.slider("Day of week", 0, 6, 2, key=f"{prefix}_dow")
        month = st.slider("Month", 1, 12, 6, key=f"{prefix}_month")
        is_weekend = st.selectbox("Weekend", [0, 1], index=0, key=f"{prefix}_weekend")
    with c2:
        demand_lag_1h = st.number_input("Demand lag 1h", 0.0, 50000.0, 28500.0, step=100.0, key=f"{prefix}_d1")
        demand_lag_24h = st.number_input("Demand lag 24h", 0.0, 50000.0, 29000.0, step=100.0, key=f"{prefix}_d24")
        demand_lag_168h = st.number_input("Demand lag 168h", 0.0, 50000.0, 27800.0, step=100.0, key=f"{prefix}_d168")
    with c3:
        price_lag_1h = st.number_input("Price lag 1h", 0.0, 1000.0, 52.3, step=0.1, key=f"{prefix}_p1")
        price_lag_24h = st.number_input("Price lag 24h", 0.0, 1000.0, 48.7, step=0.1, key=f"{prefix}_p24")
        demand_avg_24h = st.number_input("Demand avg 24h", 0.0, 50000.0, 28200.0, step=100.0, key=f"{prefix}_davg")
        price_avg_24h = st.number_input("Price avg 24h", 0.0, 1000.0, 50.1, step=0.1, key=f"{prefix}_pavg")
    with c4:
        solar = st.number_input("Solar", 0.0, 20000.0, 5000.0, step=100.0, key=f"{prefix}_solar")
        wind = st.number_input("Wind", 0.0, 30000.0, 8000.0, step=100.0, key=f"{prefix}_wind")
        gas = st.number_input("Fossil gas", 0.0, 20000.0, 4000.0, step=100.0, key=f"{prefix}_gas")
        coal = st.number_input("Fossil coal", 0.0, 20000.0, 1500.0, step=100.0, key=f"{prefix}_coal")
        hydro = st.number_input("Hydro", 0.0, 20000.0, 2000.0, step=100.0, key=f"{prefix}_hydro")
        nuclear = st.number_input("Nuclear", 0.0, 20000.0, 7000.0, step=100.0, key=f"{prefix}_nuclear")

    renewable = solar + wind + hydro
    fossil = gas + coal
    total_gen = renewable + fossil + nuclear
    renewable_pct = (renewable / total_gen * 100.0) if total_gen else 0.0

    return {
        "hour": hour,
        "day_of_week": day_of_week,
        "month": month,
        "is_weekend": int(is_weekend),
        "demand_lag_1h": demand_lag_1h,
        "demand_lag_24h": demand_lag_24h,
        "demand_lag_168h": demand_lag_168h,
        "price_lag_1h": price_lag_1h,
        "price_lag_24h": price_lag_24h,
        "renewable": renewable,
        "fossil": fossil,
        "nuclear": nuclear,
        "renewable_pct": renewable_pct,
        "demand_avg_24h": demand_avg_24h,
        "price_avg_24h": price_avg_24h,
        "forecast wind onshore day ahead": wind,
        "forecast solar day ahead": solar,
        "total load forecast": demand_avg_24h,
        "price day ahead": price_avg_24h,
    }


def _clean_rule_text(x):
    if isinstance(x, list):
        return ", ".join([str(v) for v in x])
    if isinstance(x, str):
        parts = [p.strip() for p in x.replace("\n", ",").replace("|", ",").split(",") if p.strip()]
        return ", ".join(parts)
    return str(x)


tabs = st.tabs([
    "Live Prediction",
    "12h Forecast",
    "Model Comparison",
    "Cluster Explorer",
    "Association Rules",
])

with tabs[0]:
    st.subheader("Live Prediction")
    payload = _inputs("live")
    if st.button("Predict Live", key="live_predict"):
        pred = predict_both(payload)
        cls = classify_demand(payload)
        if pred:
            c1, c2, c3 = st.columns(3)
            c1.metric("Demand", f"{pred.get('predicted_demand_12h_MW', 0):,.1f} MW")
            c2.metric("Price", f"{pred.get('predicted_price_12h_EUR', 0):,.2f} EUR/MWh")
            c3.metric("Demand Class", str((cls or {}).get("demand_class", "N/A")))
        else:
            st.warning("Prediction failed. Check backend.")

with tabs[1]:
    st.subheader("12h Forecast")
    payload = _inputs("f12")
    if st.button("Generate 12h Forecast", key="forecast_12h"):
        rows = []
        for step in range(12):
            p = dict(payload)
            hour = (int(payload["hour"]) + step) % 24
            day_offset = (int(payload["hour"]) + step) // 24
            p["hour"] = hour
            p["day_of_week"] = (int(payload["day_of_week"]) + day_offset) % 7
            res = predict_both(p)
            if not res:
                continue
            rows.append(
                {
                    "step": step + 1,
                    "hour": hour,
                    "demand": float(res.get("predicted_demand_12h_MW", 0.0)),
                    "price": float(res.get("predicted_price_12h_EUR", 0.0)),
                }
            )
        if rows:
            df = pd.DataFrame(rows)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df["step"], y=df["demand"], mode="lines+markers", name="Demand (MW)", line=dict(color=COLORS["accent_teal"])))
            fig.add_trace(go.Scatter(x=df["step"], y=df["price"], mode="lines+markers", name="Price (EUR/MWh)", yaxis="y2", line=dict(color=COLORS["accent_amber"])))
            fig.update_layout(
                xaxis_title="Forecast step (next 12 calls)",
                yaxis_title="Demand (MW)",
                yaxis2=dict(title="Price (EUR/MWh)", overlaying="y", side="right"),
                paper_bgcolor=COLORS["bg_card"],
                plot_bgcolor=COLORS["bg_card"],
                font=dict(color=COLORS["text_primary"]),
            )
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.warning("No forecast points returned from API.")

with tabs[2]:
    st.subheader("Model Comparison")
    registry = get_model_registry()
    metrics = get_model_comparison()

    if metrics:
        rows = []
        for model_name, vals in metrics.items():
            rows.append(
                {
                    "Model": model_name,
                    "Demand R2": float(vals.get("demand_r2", 0.0)),
                    "Price R2": float(vals.get("price_r2", 0.0)),
                    # API currently returns NMAE; use as error proxy if RMSE is unavailable.
                    "Demand Error": float(vals.get("demand_nmae", vals.get("demand_rmse", 0.0))),
                    "Price Error": float(vals.get("price_nmae", vals.get("price_rmse", 0.0))),
                    "Avg R2": float(vals.get("avg_r2", 0.0)),
                }
            )
        mdf = pd.DataFrame(rows).sort_values("Avg R2", ascending=False)
        c1, c2 = st.columns(2)
        with c1:
            fig_r2 = px.bar(mdf, x="Model", y="Avg R2", title="Model Ranking by Avg R2", color="Avg R2", color_continuous_scale="Viridis")
            st.plotly_chart(fig_r2, use_container_width=True)
        with c2:
            fig_err = go.Figure()
            fig_err.add_trace(go.Bar(x=mdf["Model"], y=mdf["Demand Error"], name="Demand Error"))
            fig_err.add_trace(go.Bar(x=mdf["Model"], y=mdf["Price Error"], name="Price Error"))
            fig_err.update_layout(barmode="group", title="Error Metric (NMAE or RMSE when available)")
            st.plotly_chart(fig_err, use_container_width=True)
        st.dataframe(mdf, use_container_width=True, hide_index=True)
    else:
        st.warning("Model metrics endpoint unavailable.")

    if registry:
        st.caption("Registry source: /models/compare")
        st.json({
            "regression_model_demand": registry.get("regression_model_demand"),
            "regression_model_price": registry.get("regression_model_price"),
            "classifier_demand": registry.get("classifier_demand"),
            "classifier_price": registry.get("classifier_price"),
            "clustering_model": registry.get("clustering_model"),
            "n_clusters": registry.get("n_clusters"),
        })

with tabs[3]:
    st.subheader("Cluster Explorer")
    profiles = get_cluster_profiles()
    if profiles:
        cdf = pd.DataFrame(profiles).T if isinstance(profiles, dict) else pd.DataFrame(profiles)
        st.dataframe(cdf, use_container_width=True)
        if {"pred_demand", "pred_price"}.issubset(cdf.columns):
            cdf = cdf.reset_index().rename(columns={"index": "cluster"})
            fig = px.scatter(
                cdf,
                x="pred_demand",
                y="pred_price",
                size="renewable_pct" if "renewable_pct" in cdf.columns else None,
                color="cluster",
                hover_name="cluster",
                title="Cluster Regime Map",
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Cluster profiles unavailable.")

with tabs[4]:
    st.subheader("Association Rules")

    t1, t2 = st.columns([2, 1])
    with t2:
        n = st.slider("Top N", 5, 50, 20)
    top_rules = get_top_associations(n=n)
    if top_rules:
        rules = top_rules if isinstance(top_rules, list) else top_rules.get("rules", [])
        if rules:
            rdf = pd.DataFrame(rules)
            if "antecedents" in rdf.columns:
                rdf["antecedents"] = rdf["antecedents"].apply(_clean_rule_text)
            if "consequents" in rdf.columns:
                rdf["consequents"] = rdf["consequents"].apply(_clean_rule_text)
            st.dataframe(rdf, use_container_width=True, hide_index=True)
        else:
            st.info("No top rules returned.")

    st.markdown("#### Filter Rules")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        demand_level = st.selectbox("Demand", [None, "LOW", "MED", "HIGH"], index=0)
    with c2:
        price_level = st.selectbox("Price", [None, "LOW", "MED", "HIGH"], index=0)
    with c3:
        renewable_level = st.selectbox("Renewable", [None, "LOW", "MED", "HIGH"], index=0)
    with c4:
        qn = st.number_input("Top N", 1, 20, 5)

    if st.button("Run Rule Query"):
        res = query_associations(demand_level=demand_level, price_level=price_level, renewable_level=renewable_level, top_n=int(qn))
        if res and res.get("rules"):
            qdf = pd.DataFrame(res["rules"])
            if "antecedents" in qdf.columns:
                qdf["antecedents"] = qdf["antecedents"].apply(_clean_rule_text)
            if "consequents" in qdf.columns:
                qdf["consequents"] = qdf["consequents"].apply(_clean_rule_text)
            st.dataframe(qdf, use_container_width=True, hide_index=True)
        elif res and res.get("debug"):
            st.warning("Rule query fallback diagnostics:")
            st.json(res.get("debug"))
        else:
            st.info("No matching rules.")
