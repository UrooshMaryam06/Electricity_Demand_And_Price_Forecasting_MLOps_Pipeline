"""
Dataset explorer: raw data preview, distributions, correlations, generation mix.
"""
import streamlit as st
import plotly.express as px
st.set_page_config(page_title="Data Explorer", layout="wide")

with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

from components.sidebar import render_sidebar
from services.data_loader import load_dataset
from components.charts import correlation_heatmap, generation_mix_pie
from utils.config import COLORS, GENERATION_FEATURES

render_sidebar()
st.markdown("## Data Explorer")
st.divider()

df = load_dataset()
if df.empty:
    st.error("Dataset not found.")
    st.stop()

start, end = st.session_state.get("date_range", (df.index.min().date(), df.index.max().date()))
mask = (df.index.date >= start) & (df.index.date <= end)
view = df[mask]

# ── Summary stats ─────────────────────────────────────────────────────────────
st.markdown(f"Showing **{len(view):,}** rows from {start} to {end}")

tab1, tab2, tab3, tab4 = st.tabs([
    "Raw Data", "Distributions", "Correlation", "Generation Mix"
])

with tab1:
    st.dataframe(
        view[['total load actual', 'price actual',
              'generation solar', 'generation wind onshore',
              'generation nuclear', 'generation fossil gas']].head(500),
        use_container_width=True,
    )

with tab2:
    feature = st.selectbox(
        "Feature to plot",
        ["total load actual", "price actual", "renewable_pct"] + GENERATION_FEATURES,
    )
    fig = px.histogram(
        view.reset_index(), x=feature, nbins=60,
        color_discrete_sequence=[COLORS["accent_teal"]],
        title=f"Distribution: {feature}",
    )
    fig.update_layout(
        paper_bgcolor=COLORS["bg_card"], plot_bgcolor=COLORS["bg_card"],
        font=dict(color=COLORS["text_primary"]),
    )
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    corr_cols = ["total load actual", "price actual", "renewable_pct",
                 "generation solar", "generation wind onshore",
                 "generation fossil gas", "generation nuclear"]
    available = [c for c in corr_cols if c in view.columns]
    fig = correlation_heatmap(view, available)
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    sample_row = view.iloc[len(view) // 2]   # middle row as a representative sample
    fig = generation_mix_pie(sample_row)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Generation mix at midpoint of selected date range.")
