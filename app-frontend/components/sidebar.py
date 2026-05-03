import streamlit as st
import pandas as pd
from services.data_loader import load_dataset


def render_sidebar():
    """
    Renders the global sidebar and populates st.session_state with:
      - date_range: (start_date, end_date) tuple
      - selected_hour: int 0-23
      - api_url: str
    """
    with st.sidebar:
        st.markdown("## Electricity Forecasting")
        st.caption("MLOps Pipeline Dashboard")
        st.divider()

        # Date range filter (for historical charts)
        df = load_dataset()
        if not df.empty:
            min_date = df.index.min().date()
            max_date = df.index.max().date()
        else:
            min_date = pd.Timestamp("2015-01-01").date()
            max_date = pd.Timestamp("2018-12-31").date()

        start_date = st.date_input(
            "Start date", value=pd.Timestamp("2018-01-01").date(),
            min_value=min_date, max_value=max_date
        )
        end_date = st.date_input(
            "End date", value=max_date,
            min_value=start_date, max_value=max_date
        )
        st.session_state["date_range"] = (start_date, end_date)

        st.divider()

        # Hour selector for predictions
        hour = st.slider("Hour of day (for predictions)", 0, 23,
                          value=st.session_state.get("selected_hour", 12))
        st.session_state["selected_hour"] = hour

        st.divider()

        # API status indicator
        from services.api_client import get_health
        health = get_health()
        if health:
            st.success("API: Online")
        else:
            st.error("API: Offline")

        st.caption(f"API: {st.session_state.get('api_url', 'localhost:8000')}")
