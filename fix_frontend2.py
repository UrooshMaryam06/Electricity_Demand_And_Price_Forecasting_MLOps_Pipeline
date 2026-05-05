# Fix 1: raw_input_form.py — replace BOTH expanders with plain sections
with open('/app/components/raw_input_form.py', 'r') as f:
    content = f.read()

old = '    with st.expander("Lag Features", expanded=False):'
new = '    st.markdown("##### Lag Features")\n    if True:'

if old in content:
    content = content.replace(old, new)
    print("Fix 1 applied: Lag Features expander removed")
else:
    print("Fix 1 ERROR: pattern not found")

with open('/app/components/raw_input_form.py', 'w') as f:
    f.write(content)

# Fix 2: api_client.py — get_model_comparison should call compare_metrics
with open('/app/services/api_client.py', 'r') as f:
    content = f.read()

old = '''def get_model_comparison() -> dict | None:
    """GET /models/compare — returns model registry info."""
    return _get("/models/compare")'''

new = '''def get_model_comparison() -> dict | None:
    """GET /models/compare_metrics — returns per-model performance metrics."""
    return _get("/models/compare_metrics")'''

if old in content:
    content = content.replace(old, new)
    print("Fix 2 applied: get_model_comparison now calls /models/compare_metrics")
else:
    # try alternate spacing
    old2 = 'def get_model_comparison() -> dict | None:\n    """GET /models/compare — returns model registry info."""\n    return _get("/models/compare")'
    if old2 in content:
        content = content.replace(old2, new)
        print("Fix 2 applied (alternate): get_model_comparison fixed")
    else:
        print("Fix 2 ERROR: pattern not found, printing context...")
        idx = content.find("get_model_comparison")
        print(repr(content[idx:idx+200]))

with open('/app/services/api_client.py', 'w') as f:
    f.write(content)

print("\nAll fixes done.")
