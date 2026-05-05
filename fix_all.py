# ── Fix 1: api_client.py — point get_model_comparison to correct endpoint ────
f = open('/app/services/api_client.py')
c = f.read()
f.close()

c = c.replace(
    '"""GET /models/compare — returns model registry info."""\n    return _get("/models/compare")',
    '"""GET /models/compare_metrics — returns per-model metrics."""\n    return _get("/models/compare_metrics")'
)

f = open('/app/services/api_client.py', 'w')
f.write(c)
f.close()
print('Fix 1 DONE: api_client.py now calls /models/compare_metrics')

# ── Fix 2: 0_ML_Dashboard.py — remove broken continue, apply correct fix ─────
f = open('/app/pages/0_ML_Dashboard.py')
c = f.read()
f.close()

# Remove the bad inline continue that broke syntax
c = c.replace(
    '        if not isinstance(vals, dict): continue\n        rows.append(',
    '        rows.append('
)

# Apply correct multi-line fix
c = c.replace(
    '        for model_name, vals in metrics.items():\n            rows.append(',
    '        for model_name, vals in metrics.items():\n            if not isinstance(vals, dict):\n                continue\n            rows.append('
)

f = open('/app/pages/0_ML_Dashboard.py', 'w')
f.write(c)
f.close()
print('Fix 2 DONE: 0_ML_Dashboard.py continue fixed')

# ── Fix 3: 1_Overview.py — isinstance guard ───────────────────────────────────
f = open('/app/pages/1_Overview.py')
c = f.read()
f.close()

c = c.replace(
    '    models = list(comparison.keys())',
    '    models = [m for m in comparison if isinstance(comparison[m], dict)]'
)

f = open('/app/pages/1_Overview.py', 'w')
f.write(c)
f.close()
print('Fix 3 DONE: 1_Overview.py isinstance guard added')

# ── Fix 4: 3_Model_Comparison.py — isinstance guard ──────────────────────────
f = open('/app/pages/3_Model_Comparison.py')
c = f.read()
f.close()

c = c.replace(
    'for model_name, metrics in data.items():\n    # Support multiple',
    'for model_name, metrics in data.items():\n    if not isinstance(metrics, dict):\n        continue\n    # Support multiple'
)

f = open('/app/pages/3_Model_Comparison.py', 'w')
f.write(c)
f.close()
print('Fix 4 DONE: 3_Model_Comparison.py isinstance guard added')

# ── Fix 5: Classification page — add timestamp to payload ────────────────────
f = open('/app/pages/5_Classification.py')
c = f.read()
f.close()

# The API requires timestamp field — inject it from time_str if missing
old = 'raw = render_raw_input_form(key_prefix="classify_")'
new = '''raw = render_raw_input_form(key_prefix="classify_")
raw["timestamp"] = raw.get("time_str", "2018-06-15 14:00:00")'''

if 'raw["timestamp"]' not in c:
    c = c.replace(old, new)

f = open('/app/pages/5_Classification.py', 'w')
f.write(c)
f.close()
print('Fix 5 DONE: 5_Classification.py timestamp injected')

# ── Fix 6: Forecasting page — same timestamp fix ─────────────────────────────
f = open('/app/pages/2_Forecasting.py')
c = f.read()
f.close()

old = 'raw = render_raw_input_form(key_prefix="forecast_")'
new = '''raw = render_raw_input_form(key_prefix="forecast_")
raw["timestamp"] = raw.get("time_str", "2018-06-15 14:00:00")'''

if 'raw["timestamp"]' not in c:
    c = c.replace(old, new)

f = open('/app/pages/2_Forecasting.py', 'w')
f.write(c)
f.close()
print('Fix 6 DONE: 2_Forecasting.py timestamp injected')

print('\nAll fixes applied successfully!')
