"""
Clustering page: show cluster profiles and PCA scatter from the saved artifacts.
"""
from pathlib import Path

import streamlit as st
import pandas as pd
import numpy as np
st.set_page_config(page_title="Clustering", layout="wide")

with open(Path(__file__).resolve().parents[1] / "assets" / "style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

from components.sidebar import render_sidebar
from services.api_client import get_cluster_profiles
from services.data_loader import load_dataset
from components.charts import pca_scatter
from utils.config import COLORS

render_sidebar()
st.markdown("## Energy Regime Clustering")
st.caption("KMeans clustering groups hourly grid states into operational regimes.")
st.divider()

profiles = get_cluster_profiles()
if profiles:
    st.markdown("### Cluster Profiles")
    profile_df = pd.DataFrame(profiles).T if isinstance(profiles, dict) else pd.DataFrame(profiles)
    st.dataframe(profile_df, use_container_width=True)
else:
    st.warning("Cluster profiles not available from API.")

# ── PCA scatter from local data ───────────────────────────────────────────────
st.divider()
st.markdown("### PCA Visualization")

df = load_dataset()
if not df.empty:
    from sklearn.preprocessing import StandardScaler
    from sklearn.decomposition import PCA
    import warnings
    warnings.filterwarnings("ignore")

    feature_cols = [
        'total load actual', 'price actual', 'renewable_pct',
        'generation solar', 'generation wind onshore',
        'generation fossil gas', 'generation nuclear', 'hour', 'month'
    ]
    available = [c for c in feature_cols if c in df.columns]
    sample = df[available].dropna().sample(min(3000, len(df)), random_state=42)

    scaler = StandardScaler()
    X_sc = scaler.fit_transform(sample)

    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_sc)

    from sklearn.cluster import KMeans
    km = KMeans(n_clusters=4, random_state=42, n_init=10)
    cluster_labels = km.fit_predict(X_sc)

    explained = pca.explained_variance_ratio_ * 100
    fig = pca_scatter(
        x=X_pca[:, 0].tolist(),
        y=X_pca[:, 1].tolist(),
        labels=cluster_labels.tolist(),
    )
    fig.update_layout(
        xaxis_title=f"PC1 ({explained[0]:.1f}% variance)",
        yaxis_title=f"PC2 ({explained[1]:.1f}% variance)",
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        f"PCA explains {sum(explained):.1f}% of total variance across two components. "
        f"Sample: {len(sample):,} rows."
    )
