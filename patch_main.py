with open('/app/main_new_v2.py', 'r') as f:
    content = f.read()

# Add reg_demand_features and reg_price_features loading after existing loads
old = "demand_features = load('demand_features.pkl')\nprice_features  = load('price_features.pkl')"
new = """demand_features = load('demand_features.pkl')
price_features  = load('price_features.pkl')
reg_demand_features = load('reg_demand_features.pkl')
reg_price_features  = load('reg_price_features.pkl')"""

if old in content:
    content = content.replace(old, new)
    print("Fix 1 applied: reg feature lists added to loader")
else:
    print("ERROR: Fix 1 pattern not found - trying alternate...")
    old2 = "demand_features = load('demand_features.pkl')\nprice_features = load('price_features.pkl')"
    new2 = """demand_features = load('demand_features.pkl')
price_features = load('price_features.pkl')
reg_demand_features = load('reg_demand_features.pkl')
reg_price_features  = load('reg_price_features.pkl')"""
    if old2 in content:
        content = content.replace(old2, new2)
        print("Fix 1 applied (alternate): reg feature lists added")
    else:
        print("ERROR: Could not find loader pattern. Print nearby lines:")
        idx = content.find("demand_features")
        print(repr(content[idx-5:idx+120]))

# Fix predict_demand to use reg_demand_features
old3 = "def predict_demand(raw: dict) -> float:\n    raw = extract_features(raw)\n    X   = build_feature_row(raw, demand_features)"
new3 = "def predict_demand(raw: dict) -> float:\n    raw = extract_features(raw)\n    X   = build_feature_row(raw, reg_demand_features)"

if old3 in content:
    content = content.replace(old3, new3)
    print("Fix 2 applied: predict_demand uses reg_demand_features")
else:
    print("ERROR: Fix 2 pattern not found")

# Fix predict_price to use reg_price_features
old4 = "def predict_price(raw: dict) -> float:\n    raw = extract_features(raw)\n    X   = build_feature_row(raw, price_features)"
new4 = "def predict_price(raw: dict) -> float:\n    raw = extract_features(raw)\n    X   = build_feature_row(raw, reg_price_features)"

if old4 in content:
    content = content.replace(old4, new4)
    print("Fix 3 applied: predict_price uses reg_price_features")
else:
    print("ERROR: Fix 3 pattern not found")

with open('/app/main_new_v2.py', 'w') as f:
    f.write(content)

print("All done.")
