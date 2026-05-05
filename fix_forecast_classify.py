# Fix 1: 2_Forecasting.py — remove outer expander (causes nesting) + fix predict call
f = open('/app/pages/2_Forecasting.py')
c = f.read()
f.close()

# Remove the outer expander wrapper that causes nesting crash
c = c.replace(
    'with st.expander("Input Features", expanded=True):\n    raw = render_raw_input_form(key_prefix="forecast_")',
    'raw = render_raw_input_form(key_prefix="forecast_")'
)

# Fix predict_both call — it needs raw dict with timestamp, not pre-engineered features
c = c.replace(
    '    result = predict_both(demand_features)',
    '    _payload = dict(raw)\n    _payload["timestamp"] = raw.get("time_str", "2018-06-15 14:00:00")\n    result = predict_both(_payload)'
)

f = open('/app/pages/2_Forecasting.py', 'w')
f.write(c)
f.close()
print('Fix 1 DONE: 2_Forecasting.py fixed')

# Fix 2: 5_Classification.py — check what it sends and fix timestamp
f = open('/app/pages/5_Classification.py')
c = f.read()
f.close()
print('--- Classification payload lines ---')
for i, line in enumerate(c.split('\n')):
    if 'classify' in line.lower() or 'timestamp' in line.lower() or 'payload' in line.lower() or 'raw' in line.lower():
        print(f'{i+1}: {line}')
f.close()

# Ensure timestamp is in raw before any classify call
old = 'raw = render_raw_input_form(key_prefix="classify_")\nraw["timestamp"] = raw.get("time_str", "2018-06-15 14:00:00")'
if old not in c:
    c = c.replace(
        'raw = render_raw_input_form(key_prefix="classify_")',
        'raw = render_raw_input_form(key_prefix="classify_")\nraw["timestamp"] = raw.get("time_str", "2018-06-15 14:00:00")'
    )

f = open('/app/pages/5_Classification.py', 'w')
f.write(c)
f.close()
print('Fix 2 DONE: 5_Classification.py fixed')

# Fix 3: verify what classify calls look like now
f = open('/app/pages/5_Classification.py')
c = f.read()
f.close()
for i, line in enumerate(c.split('\n')):
    if 'classify' in line.lower() or 'timestamp' in line.lower():
        print(f'{i+1}: {line}')
