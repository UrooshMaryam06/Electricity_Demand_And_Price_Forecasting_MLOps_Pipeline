"""
Pipeline monitor: shows Prefect flow run history.
If the Prefect API is not running, displays the last known run from a local log.
"""
import streamlit as st
import requests
import pandas as pd
from pathlib import Path
st.set_page_config(page_title="Pipeline Monitor", layout="wide")

with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

from components.sidebar import render_sidebar
from utils.config import COLORS

render_sidebar()
st.markdown("## Pipeline Monitor")
st.caption("Prefect orchestration status for the energy forecasting pipeline.")
st.divider()

PREFECT_API = "http://localhost:4200/api"


def load_local_pipeline_snapshot() -> dict:
    """Load last-known pipeline metadata when Prefect API is unavailable."""
    meta_path = Path("../artifacts/model_metadata.json")
    if not meta_path.exists():
        return {
            "available": False,
            "message": "No local pipeline metadata found yet.",
        }

    try:
        import json
        with open(meta_path, "r", encoding="utf8") as f:
            meta = json.load(f)
        return {
            "available": True,
            "message": "Loaded from artifacts/model_metadata.json",
            "updated": pd.to_datetime(meta_path.stat().st_mtime, unit="s"),
            "metadata": meta,
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
