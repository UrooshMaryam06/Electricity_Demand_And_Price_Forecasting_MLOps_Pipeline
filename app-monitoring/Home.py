from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Monitoring", layout="wide")

ARTIFACT_DIR = Path(__file__).resolve().parents[1] / "artifacts"

with open(Path(__file__).resolve().parents[1] / "app-frontend" / "assets" / "style.css", encoding="utf8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("Pipeline and Experiment Monitoring")
st.caption("Operational log of trained models, metrics, and pipeline metadata.")

log_json = ARTIFACT_DIR / "experiment_log.json"
log_csv = ARTIFACT_DIR / "experiment_log.csv"
log_models = ARTIFACT_DIR / "experiment_models.csv"
meta_json = ARTIFACT_DIR / "model_metadata.json"

if log_json.exists():
    with open(log_json, "r", encoding="utf8") as f:
        experiment_log = json.load(f)

    st.subheader("Top-level outcomes")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Best Demand Model", experiment_log.get("best_models", {}).get("demand", {}).get("model", "N/A"))
    c2.metric("Best Price Model", experiment_log.get("best_models", {}).get("price", {}).get("model", "N/A"))
    c3.metric("Chosen Clusters", str(experiment_log.get("clustering", {}).get("chosen_k", "N/A")))
    c4.metric("Logged Models", str(len(experiment_log.get("all_trained_models", []))))

    st.subheader("All trained models")
    if log_models.exists():
        st.dataframe(pd.read_csv(log_models), use_container_width=True, hide_index=True)
    else:
        st.dataframe(pd.DataFrame(experiment_log.get("all_trained_models", [])), use_container_width=True, hide_index=True)

    st.subheader("Experiment summary")
    if log_csv.exists():
        st.dataframe(pd.read_csv(log_csv), use_container_width=True, hide_index=True)

    st.subheader("Observations")
    st.write(experiment_log.get("observations", {}))

    md_path = ARTIFACT_DIR / "experiment_log.md"
    if md_path.exists():
        st.markdown(md_path.read_text(encoding="utf8"))
else:
    st.warning("experiment_log.json is not available yet. Run the training notebook to generate it.")

if meta_json.exists():
    st.subheader("Pipeline metadata")
    with open(meta_json, "r", encoding="utf8") as f:
        st.json(json.load(f))
else:
    st.info("model_metadata.json is not available yet.")
