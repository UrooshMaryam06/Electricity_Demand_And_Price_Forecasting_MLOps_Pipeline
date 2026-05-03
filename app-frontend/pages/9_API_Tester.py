"""
API Tester: send raw JSON to any FastAPI endpoint and see the response.
Also measures latency.
"""
import streamlit as st
import requests, json, time
st.set_page_config(page_title="API Tester", layout="wide")

with open("assets/style.css") as f:
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

DEFAULT_FEATURES = json.dumps({
    "hour": 14, "month": 6, "is_weekend": 0,
    "generation solar": 5000.0, "generation wind onshore": 8000.0,
    "generation fossil gas": 4000.0, "generation nuclear": 7000.0,
    "generation fossil hard coal": 1500.0,
    "generation hydro water reservoir": 2000.0,
    "demand_lag_1h": 28000.0, "demand_lag_24h": 27500.0, "demand_lag_168h": 27000.0,
    "price_lag_1h": 50.0, "price_lag_24h": 48.0,
    "total_load_forecast": 28500.0,
}, indent=2)

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
