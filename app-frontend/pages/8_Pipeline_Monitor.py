"""
Pipeline monitor: shows Prefect flow run history.
If the Prefect API is not running, displays the last known run from local logs.
"""
import json
from pathlib import Path

import pandas as pd
import requests
import streamlit as st
st.set_page_config(page_title="Pipeline Monitor", layout="wide")

with open(Path(__file__).resolve().parents[1] / "assets" / "style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

from components.sidebar import render_sidebar
from utils.config import COLORS

render_sidebar()
st.markdown("## Pipeline Monitor")
st.caption("Prefect orchestration status for the energy forecasting pipeline.")
st.divider()

PREFECT_API = "http://localhost:4200/api"


def load_local_pipeline_snapshot() -> dict:
    """Load last-known pipeline metadata and experiment logs when Prefect API is unavailable."""
    meta_path = Path("../artifacts/model_metadata.json")
    exp_path = Path("../artifacts/experiment_log.json")
    if not meta_path.exists():
        snapshot = {
            "available": False,
            "message": "No local pipeline metadata found yet.",
        }
        if exp_path.exists():
            try:
                with open(exp_path, "r", encoding="utf8") as f:
                    snapshot["experiment_log"] = json.load(f)
                snapshot["available"] = True
                snapshot["message"] = "Loaded experiment_log.json"
            except Exception as e:
                snapshot["experiment_error"] = str(e)
        return snapshot

    try:
        with open(meta_path, "r", encoding="utf8") as f:
            meta = json.load(f)
        exp_log = None
        if exp_path.exists():
            with open(exp_path, "r", encoding="utf8") as f:
                exp_log = json.load(f)
        return {
            "available": True,
            "message": "Loaded from artifacts/model_metadata.json",
            "updated": pd.to_datetime(meta_path.stat().st_mtime, unit="s"),
            "metadata": meta,
            "experiment_log": exp_log,
        }
    except Exception as e:
        return {
            "available": False,
            "message": f"Failed to read local metadata: {e}",
        }

@st.cache_data(ttl=30)
def get_prefect_flow_runs():
    """Query Prefect API for recent flow runs."""
    try:
        r = requests.post(
            f"{PREFECT_API}/flow_runs/filter",
            json={"limit": 20, "sort": "START_TIME_DESC"},
            timeout=5,
        )
        r.raise_for_status()
        payload = r.json()
        # Prefect may return either a list or an object with a flow_runs key.
        if isinstance(payload, list):
            return payload
        if isinstance(payload, dict):
            return payload.get("flow_runs", [])
        return []
    except Exception as e:
        return {"error": str(e), "flow_runs": None}


flow_runs = get_prefect_flow_runs()

if isinstance(flow_runs, dict) and flow_runs.get("flow_runs") is None:
    st.info(
        "Prefect API is offline at localhost:4200. "
        "Run `prefect server start` if you want live orchestration status."
    )

    local_snapshot = load_local_pipeline_snapshot()
    if local_snapshot.get("available"):
        st.success(local_snapshot.get("message", "Local snapshot loaded."))
        updated = local_snapshot.get("updated")
        if updated is not None:
            st.caption(f"Last metadata update: {updated}")
        meta = local_snapshot.get("metadata", {})
        st.json(meta)

        exp_log = local_snapshot.get("experiment_log")
        if exp_log:
            st.markdown("### Experiment Log")
            c1, c2, c3 = st.columns(3)
            c1.metric("Best Demand Model", exp_log.get("best_models", {}).get("demand", {}).get("model", "N/A"))
            c2.metric("Best Price Model", exp_log.get("best_models", {}).get("price", {}).get("model", "N/A"))
            c3.metric("Chosen Clusters", str(exp_log.get("clustering", {}).get("chosen_k", "N/A")))

            observations = exp_log.get("observations", {})
            st.markdown("#### Observations")
            st.write("Best-performing model:", observations.get("best_performing_model", "N/A"))
            st.write("Data quality issues:")
            st.write(observations.get("data_quality_issues", []))
            st.write("Overfitting / underfitting patterns:")
            st.write(observations.get("overfitting_patterns", []))
            st.write("Deployment speed:", observations.get("deployment_speed", "N/A"))
            st.write("Prefect reliability:", observations.get("prefect_reliability", "N/A"))

            md_path = Path("../artifacts/experiment_log.md")
            if md_path.exists():
                with open(md_path, "r", encoding="utf8") as f:
                    st.markdown("#### Experiment Log Notes")
                    st.markdown(f.read())
    else:
        st.caption(local_snapshot.get("message", ""))

    st.markdown("""
    **Pipeline steps (from `train_pipeline.py`):**

    | Step | Task | Status |
    |------|------|--------|
    | 1 | load_data | Defined |
    | 2 | preprocess | Defined |
    | 3 | train_model | Defined |
    | 4 | create_thresholds | Defined |
    | 5 | save_artifacts | Defined |
    | 6 | run_association_task | Defined |
    """)
else:
    st.markdown(f"**{len(flow_runs)} recent flow runs**")
    rows = []
    for run in flow_runs:
        state = run.get("state", {})
        rows.append({
            "Name":       run.get("name", ""),
            "State":      state.get("type", "UNKNOWN"),
            "Started":    run.get("start_time", ""),
            "Duration":   f"{run.get('total_run_time', 0):.1f}s",
            "Flow":       run.get("flow_name", ""),
        })

    runs_df = pd.DataFrame(rows)

    def highlight_state(val):
        if val == "COMPLETED":
            return f"color: {COLORS['accent_green']}"
        elif val == "FAILED":
            return f"color: {COLORS['accent_red']}"
        elif val == "RUNNING":
            return f"color: {COLORS['accent_amber']}"
        return ""

    st.dataframe(
        runs_df.style.applymap(highlight_state, subset=["State"]),
        use_container_width=True,
        hide_index=True,
    )
