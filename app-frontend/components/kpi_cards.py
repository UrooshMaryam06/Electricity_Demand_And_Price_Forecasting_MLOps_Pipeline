import streamlit as st
from utils.config import COLORS


def render_kpi_row(metrics: list[dict]):
    """
    Render a row of KPI cards.

    metrics: list of dicts with keys:
        label (str), value (str|float), delta (str, optional),
        delta_color ('normal'|'inverse'|'off', optional)

    Example:
        render_kpi_row([
            {"label": "Best R2", "value": "0.94", "delta": "+0.03 vs baseline"},
            {"label": "RMSE (demand)", "value": "1,243 MW"},
        ])
    """
    cols = st.columns(len(metrics))
    for col, m in zip(cols, metrics):
        with col:
            st.metric(
                label=m["label"],
                value=m["value"],
                delta=m.get("delta"),
                delta_color=m.get("delta_color", "normal"),
            )
