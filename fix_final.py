# ── Fix 1: 0_ML_Dashboard.py — remove the misplaced isinstance line ───────────
f = open('/app/pages/0_ML_Dashboard.py')
c = f.read()
f.close()

# Remove the bad line that got injected in the wrong place
c = c.replace(
    '            if not isinstance(vals, dict): continue\n        rows.append(',
    '        rows.append('
)

# Now find the correct model comparison loop and add the guard there
c = c.replace(
    '        for model_name, vals in metrics.items():\n            rows.append(',
    '        for model_name, vals in metrics.items():\n            if not isinstance(vals, dict):\n                continue\n            rows.append('
)

f = open('/app/pages/0_ML_Dashboard.py', 'w')
f.write(c)
f.close()
print('Fix 1 DONE: 0_ML_Dashboard.py corrected')

# ── Fix 2: 5_Classification.py — send raw+timestamp not pre-engineered features
f = open('/app/pages/5_Classification.py')
c = f.read()
f.close()

# Replace the classify calls to send raw dict (with timestamp) instead of engineered features
c = c.replace(
    '    d_result = classify_demand(demand_features)\n    p_result = classify_price(price_features)',
    '    d_result = classify_demand(raw)\n    p_result = classify_price(raw)'
)

f = open('/app/pages/5_Classification.py', 'w')
f.write(c)
f.close()
print('Fix 2 DONE: 5_Classification.py now sends raw with timestamp')

# ── Fix 3: also fix outer expander on Classification page ─────────────────────
f = open('/app/pages/5_Classification.py')
c = f.read()
f.close()

c = c.replace(
    'with st.expander("Input Features", expanded=True):\n    raw = render_raw_input_form(key_prefix="classify_")',
    'raw = render_raw_input_form(key_prefix="classify_")'
)

f = open('/app/pages/5_Classification.py', 'w')
f.write(c)
f.close()
print('Fix 3 DONE: outer expander removed from Classification')

print('\nAll done!')
