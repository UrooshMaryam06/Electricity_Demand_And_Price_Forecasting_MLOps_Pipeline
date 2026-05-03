"""
API Tester: send raw JSON to any FastAPI endpoint and see the response.
Also measures latency.
"""
from pathlib import Path

import streamlit as st
import requests, json, time
st.set_page_config(page_title="API Tester", layout="wide")

with open(Path(__file__).resolve().parents[1] / "assets" / "style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

from components.sidebar import render_sidebar
from utils.config import API_BASE_URL

render_sidebar()
st.markdown("## API Tester")
st.caption("Send live requests to the FastAPI backend and inspect responses.")
st.divider()

ENDPOINTS = {
    "GET  /health":              ("GET",  "/health",           None),
    "POST /predict/demand":      ("POST", "/predict/demand",   "features"),
    "POST /predict/price":       ("POST", "/predict/price",    "features"),
    "POST /predict/both":        ("POST", "/predict/both",     "features"),
    "POST /classify/demand":     ("POST", "/classify/demand",  "features"),
    "POST /classify/price":      ("POST", "/classify/price",   "features"),
    "POST /cluster":             ("POST", "/cluster",          "features"),
    "GET  /models/compare":      ("GET",  "/models/compare",   None),
    "GET  /recommend":           ("GET",  "/recommend",        None),
    "GET  /associations/top":    ("GET",  "/associations/top", None),
    "GET  /clusters/profiles":   ("GET",  "/clusters/profiles",None),
}

selected = st.selectbox("Endpoint", list(ENDPOINTS.keys()))
method, path, body_type = ENDPOINTS[selected]

# ── DEFAULT PAYLOAD (replaced) ────────────────────────────────────────────────
import json as _json
from services.feature_engineering import build_all_features as _baf

_sample_raw = {
    "time_str": "2018-06-15 14:00:00",
    "generation solar": 4500.0,
    "generation wind onshore": 8000.0,
    "generation hydro run-of-river and poundage": 1500.0,
    "generation hydro water reservoir": 2000.0,
    "generation hydro pumped storage consumption": 500.0,
    "generation biomass": 500.0,
    "generation other renewable": 300.0,
    "generation fossil gas": 4000.0,
    "generation fossil hard coal": 1500.0,
    "generation fossil brown coal/lignite": 200.0,
    "generation fossil oil": 100.0,
    "generation nuclear": 7000.0,
    "generation other": 400.0,
    "generation waste": 250.0,
    "forecast wind onshore day ahead": 7800.0,
    "forecast solar day ahead": 4200.0,
    "total load forecast": 28000.0,
    "demand_lag_1h": 28000.0, "demand_lag_12h": 27200.0, "demand_lag_24h": 27500.0,
    "price_lag_1h": 58.0,     "price_lag_12h": 57.0,     "price_lag_24h": 57.5,
    "demand_avg_24h": 27800.0, "price_avg_24h": 58.0,
}
_all_built = _baf(_sample_raw)
DEFAULT_FEATURES = _json.dumps(_all_built['demand_features'], indent=2)
# ── END DEFAULT PAYLOAD ───────────────────────────────────────────────────────

payload_text = None
if body_type == "features":
    payload_text = st.text_area("Request body (JSON)", value=DEFAULT_FEATURES, height=220)

if st.button("Send Request"):
    url = f"{API_BASE_URL}{path}"
    try:
        start = time.time()
        if method == "GET":
            resp = requests.get(url, timeout=10)
        else:
            payload = json.loads(payload_text) if payload_text else {}
            resp = requests.post(url, json=payload, timeout=10)
        elapsed = (time.time() - start) * 1000

        col1, col2, col3 = st.columns(3)
        col1.metric("Status Code", resp.status_code)
        col2.metric("Latency",     f"{elapsed:.1f} ms")
        col3.metric("Size",        f"{len(resp.content)} bytes")

        st.divider()
        st.markdown("**Response**")
        try:
            st.json(resp.json())
        except Exception:
            st.code(resp.text)

    except requests.exceptions.ConnectionError:
        st.error("Could not connect to API. Make sure FastAPI is running.")
    except json.JSONDecodeError:
        st.error("Invalid JSON in request body.")
