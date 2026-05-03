"""Overview landing page for the Streamlit app.

This page is intentionally different from the ML dashboard. It gives a compact
status view, quick links, and project context, while the endpoint-aligned 5-tab
dashboard remains available at `ML_Dashboard`.
"""

from __future__ import annotations

from datetime import datetime

import streamlit as st

from components.kpi_cards import render_kpi_row
from components.sidebar import render_sidebar
from services.api_client import get_health, get_model_registry, get_recommendation
from utils.config import API_BASE_URL, COLORS


st.set_page_config(
		page_title="Overview",
		layout="wide",
		initial_sidebar_state="expanded",
)

with open("assets/style.css", encoding="utf8") as f:
		st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown(
		"""
		<style>
			.overview-hero {
				padding: 1.4rem 1.5rem;
				border-radius: 18px;
				border: 1px solid #2e3347;
				background: linear-gradient(135deg, rgba(21,24,35,.96), rgba(10,12,18,.92));
				margin-bottom: 1rem;
			}
			.overview-kicker {
				font-family: 'IBM Plex Mono', monospace;
				text-transform: uppercase;
				letter-spacing: .18em;
				color: #8b91a8;
				font-size: .68rem;
				margin-bottom: .35rem;
			}
			.overview-title {
				font-family: 'IBM Plex Mono', monospace;
				font-size: 2.1rem;
				font-weight: 800;
				letter-spacing: -.03em;
				margin: 0;
				color: #e8eaf0;
			}
			.overview-subtitle {
				color: #8b91a8;
				font-size: .9rem;
				margin-top: .45rem;
				max-width: 64rem;
			}
			.nav-grid {
				display: grid;
				grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
				gap: .9rem;
				margin-top: .75rem;
			}
			.nav-card {
				border: 1px solid #2e3347;
				border-radius: 16px;
				padding: 1rem;
				background: #1a1d27;
				min-height: 140px;
			}
			.nav-card h3 {
				margin: 0 0 .35rem 0;
				color: #e8eaf0;
				font-family: 'IBM Plex Mono', monospace;
			}
			.nav-card p {
				color: #8b91a8;
				margin: 0 0 .7rem 0;
				font-size: .82rem;
				line-height: 1.45;
			}
			.nav-link {
				color: #26c6da;
				font-weight: 700;
				text-decoration: none;
			}
			.nav-link:hover {
				text-decoration: underline;
			}
			.mini-list {
				margin: 0;
				padding-left: 1rem;
				color: #cfd5e3;
				font-size: .84rem;
			}
			.mini-list li { margin-bottom: .35rem; }
		</style>
		""",
		unsafe_allow_html=True,
)

render_sidebar()

health = get_health()
registry = get_model_registry()
best = get_recommendation()

st.markdown(
		f"""
		<div class="overview-hero">
			<div class="overview-kicker">Electricity Demand & Price Forecasting</div>
			<h1 class="overview-title">Project Overview</h1>
			<div class="overview-subtitle">
				This landing page gives a fast operational snapshot, while the endpoint-aligned dashboard lives in
				<a class="nav-link" href="/ML_Dashboard">ML Dashboard</a>. Use this page for status, navigation, and a
				quick read on the pipeline.
			</div>
		</div>
		""",
		unsafe_allow_html=True,
)

if health:
		render_kpi_row(
				[
						{"label": "API Status", "value": "Online"},
						{"label": "Demand Features", "value": str(health.get("demand_features", "N/A"))},
						{"label": "Price Features", "value": str(health.get("price_features", "N/A"))},
						{"label": "Clusters", "value": str(health.get("n_clusters", "N/A"))},
				]
		)
else:
		render_kpi_row(
				[
						{"label": "API Status", "value": "Offline"},
						{"label": "Demand Features", "value": "N/A"},
						{"label": "Price Features", "value": "N/A"},
						{"label": "Clusters", "value": "N/A"},
				]
		)

col1, col2, col3 = st.columns(3)
with col1:
		st.markdown(
				"""
				<div class="nav-card">
					<h3>Start Here</h3>
					<p>Open the full 5-tab ML dashboard for live prediction, comparison, clusters, and rules.</p>
					<a class="nav-link" href="/ML_Dashboard">Go to ML Dashboard</a>
				</div>
				""",
				unsafe_allow_html=True,
		)
with col2:
		st.markdown(
				"""
				<div class="nav-card">
					<h3>Pipeline State</h3>
					<p>Use the API and registry snapshot to confirm the artifacts that are currently available.</p>
					<a class="nav-link" href="/Pipeline_Monitor">Open Pipeline Monitor</a>
				</div>
				""",
				unsafe_allow_html=True,
		)
with col3:
		st.markdown(
				"""
				<div class="nav-card">
					<h3>Experimentation</h3>
					<p>Try the raw backend endpoints directly when you need to inspect payloads and responses.</p>
					<a class="nav-link" href="/API_Tester">Open API Tester</a>
				</div>
				""",
				unsafe_allow_html=True,
		)

st.divider()

left, right = st.columns([1.2, 1])
with left:
		st.markdown("### What this app covers")
		st.markdown(
				"""
				<ul class="mini-list">
					<li>Live demand and price forecasting from FastAPI</li>
					<li>Classification and cluster interpretation from trained artifacts</li>
					<li>Association rule mining with fallback diagnostics</li>
					<li>Pipeline monitoring with offline metadata fallback</li>
				</ul>
				""",
				unsafe_allow_html=True,
		)
with right:
		st.markdown("### Current snapshot")
		if registry:
				st.write(f"Backend: {API_BASE_URL}")
				st.write(f"Recommended model: {best.get('best_model', 'N/A') if best else 'N/A'}")
				st.write(f"Model family: {registry.get('regression_model_demand', 'N/A')} / {registry.get('clustering_model', 'N/A')}")
				st.write(f"Page opened at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
		else:
				st.warning("Registry snapshot unavailable. Start the API to populate this section.")
