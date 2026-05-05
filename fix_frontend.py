import subprocess

# ─────────────────────────────────────────────
# FIX 1: raw_input_form.py — nested expanders
# Replace second st.expander with st.container
# ─────────────────────────────────────────────
with open('/app/components/raw_input_form.py', 'r') as f:
    content = f.read()

old = '    with st.expander("Rolling Average Features", expanded=False):'
new = '    st.markdown("##### Rolling Average Features")\n    if True:'

if old in content:
    content = content.replace(old, new)
    print("Fix 1 applied: nested expander removed in raw_input_form.py")
else:
    print("Fix 1 ERROR: pattern not found in raw_input_form.py")

with open('/app/components/raw_input_form.py', 'w') as f:
    f.write(content)


# ─────────────────────────────────────────────
# FIX 2: 1_Overview.py — comparison[m].get() on string
# ─────────────────────────────────────────────
with open('/app/pages/1_Overview.py', 'r') as f:
    content = f.read()

old = """if comparison:
    st.markdown("**Model Performance Summary**")
    # Parse the comparison response — adjust field names to match your API response
    models = list(comparison.keys())
    rmse_d = [comparison[m].get("demand_rmse", 0) for m in models]
    r2_d   = [comparison[m].get("demand_r2",   0) for m in models]
    fig = model_comparison_bar(models, rmse_d, r2_d, "Demand Forecasting — All Models")
    st.plotly_chart(fig, use_container_width=True)"""

new = """if comparison:
    st.markdown("**Model Performance Summary**")
    models = [m for m in comparison.keys() if isinstance(comparison[m], dict)]
    rmse_d = [float(comparison[m].get("demand_nmae", comparison[m].get("demand_rmse", 0))) for m in models]
    r2_d   = [float(comparison[m].get("demand_r2", 0)) for m in models]
    if models:
        fig = model_comparison_bar(models, rmse_d, r2_d, "Demand Forecasting — All Models")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No model metrics available yet.")"""

if old in content:
    content = content.replace(old, new)
    print("Fix 2 applied: Overview comparison[m].get() fixed")
else:
    print("Fix 2 ERROR: pattern not found in 1_Overview.py")

with open('/app/pages/1_Overview.py', 'w') as f:
    f.write(content)


# ─────────────────────────────────────────────
# FIX 3: 3_Model_Comparison.py — get_metric receives list not string
# ─────────────────────────────────────────────
with open('/app/pages/3_Model_Comparison.py', 'r') as f:
    content = f.read()

old = """    def get_metric(keys, default=0.0):
        for k in keys:
            if k in metrics:
                return metrics.get(k)
        return default"""

new = """    def get_metric(keys, default=0.0):
        if isinstance(keys, str):
            keys = [keys]
        for k in keys:
            if isinstance(metrics, dict) and k in metrics:
                return metrics[k]
        return default"""

if old in content:
    content = content.replace(old, new)
    print("Fix 3 applied: get_metric fixed in 3_Model_Comparison.py")
else:
    print("Fix 3 ERROR: pattern not found in 3_Model_Comparison.py")

with open('/app/pages/3_Model_Comparison.py', 'w') as f:
    f.write(content)


# ─────────────────────────────────────────────
# FIX 4: 0_ML_Dashboard.py — vals.get() on string
# ─────────────────────────────────────────────
with open('/app/pages/0_ML_Dashboard.py', 'r') as f:
    content = f.read()

old = """    if metrics:
        rows = []
        for model_name, vals in metrics.items():
            rows.append(
                {
                    "Model": model_name,
                    "Demand R2": float(vals.get("demand_r2", 0.0)),
                    "Price R2": float(vals.get("price_r2", 0.0)),
                    # API currently returns NMAE; use as error proxy if RMSE is unavailable.
                    "Demand Error": float(vals.get("demand_nmae", vals.get("demand_rmse", 0.0))),
                    "Price Error": float(vals.get("price_nmae", vals.get("price_rmse", 0.0))),
                    "Avg R2": float(vals.get("avg_r2", 0.0)),
                }
            )"""

new = """    if metrics:
        rows = []
        for model_name, vals in metrics.items():
            if not isinstance(vals, dict):
                continue
            rows.append(
                {
                    "Model": model_name,
                    "Demand R2": float(vals.get("demand_r2", 0.0)),
                    "Price R2": float(vals.get("price_r2", 0.0)),
                    "Demand Error": float(vals.get("demand_nmae", vals.get("demand_rmse", 0.0))),
                    "Price Error": float(vals.get("price_nmae", vals.get("price_rmse", 0.0))),
                    "Avg R2": float(vals.get("avg_r2", 0.0)),
                }
            )"""

if old in content:
    content = content.replace(old, new)
    print("Fix 4 applied: ML Dashboard vals.get() fixed")
else:
    print("Fix 4 ERROR: pattern not found in 0_ML_Dashboard.py")

with open('/app/pages/0_ML_Dashboard.py', 'w') as f:
    f.write(content)

print("\nAll fixes done.")
