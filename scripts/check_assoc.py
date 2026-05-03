import pandas as pd, json, os, re, ast

ARTIFACTS = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'artifacts'))
csv_path = os.path.join(ARTIFACTS, 'association_rules.csv')
print('CSV exists:', os.path.exists(csv_path), '->', csv_path)
if not os.path.exists(csv_path):
    raise SystemExit('association_rules.csv not found in artifacts/')

df = pd.read_csv(csv_path)
print('Columns:', df.columns.tolist())

def _safe_parse(x):
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return []
    if isinstance(x, (list, tuple, set)):
        return list(x)
    if isinstance(x, str):
        s = x.strip()
        if s.startswith(('[', '(', '{')):
            try:
                val = ast.literal_eval(s)
                if isinstance(val, (list, tuple, set)):
                    return list(val)
            except Exception:
                pass
        s = s.replace('\n', ',').replace('|', ',')
        s = re.sub(r"^[\[\(\{\]\)\}\s\'\"]+|[\[\(\{\]\)\}\s\'\"]+$", '', s)
        parts = [p.strip() for p in re.split(r'[;,\\/]|,', s) if p and p.strip()]
        return parts
    return [str(x)]

if 'antecedents' in df.columns:
    df['antecedents'] = df['antecedents'].apply(_safe_parse)
if 'consequents' in df.columns:
    df['consequents'] = df['consequents'].apply(_safe_parse)

out = df[[c for c in ['antecedents','consequents','support','confidence','lift'] if c in df.columns]].head(5)
print('First 5:', json.dumps(out.to_dict(orient='records'), indent=2))
