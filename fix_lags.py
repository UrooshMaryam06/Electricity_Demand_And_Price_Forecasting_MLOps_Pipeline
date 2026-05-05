with open('/app/main_new_v2.py', 'r') as f:
    content = f.read()

# Fix 1: inside the HIST_DF branch - add 12h lags after 24h lags
old1 = "        out['price_lag_24h'] = get_hist_val(idx_24h, 'price actual', 50.0)"
new1 = """        out['price_lag_24h'] = get_hist_val(idx_24h, 'price actual', 50.0)
        idx_12h = ts - pd.Timedelta(hours=12)
        out['demand_lag_12h'] = get_hist_val(idx_12h, 'total load actual', 28000.0)
        out['price_lag_12h']  = get_hist_val(idx_12h, 'price actual', 50.0)"""

# Fix 2: inside the else branch (no historical data)
old2 = "        out['price_lag_24h'] = 50.0"
new2 = """        out['price_lag_24h'] = 50.0
        out['demand_lag_12h'] = 28000.0
        out['price_lag_12h']  = 50.0"""

if old1 in content:
    content = content.replace(old1, new1)
    print("Fix 1 applied: 12h lags added to historical branch")
else:
    print("ERROR: Fix 1 pattern not found!")

if old2 in content:
    content = content.replace(old2, new2)
    print("Fix 2 applied: 12h lags added to fallback branch")
else:
    print("ERROR: Fix 2 pattern not found!")

with open('/app/main_new_v2.py', 'w') as f:
    f.write(content)

print("Done. Verify with: grep -n 'lag_12h' /app/main_new_v2.py")
