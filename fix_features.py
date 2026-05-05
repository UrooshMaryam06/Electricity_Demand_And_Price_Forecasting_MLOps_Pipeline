import pickle

# Exact features the XGBoost models were actually trained on
demand_features = [
    'day_of_week', 'month_sin', 'month_cos', 'is_weekend',
    'hour_sin', 'hour_cos', 'demand_lag_1h', 'demand_lag_24h',
    'price_lag_1h', 'price_lag_24h', 'renewable', 'fossil',
    'nuclear', 'renewable_pct', 'demand_avg_24h', 'price_avg_24h'
]

price_features = [
    'day_of_week', 'month_sin', 'month_cos', 'is_weekend',
    'hour_sin', 'hour_cos', 'price_lag_1h', 'price_lag_12h',
    'demand_lag_1h', 'demand_lag_12h', 'renewable', 'fossil',
    'nuclear', 'renewable_pct', 'price_avg_24h', 'demand_avg_24h'
]

with open('/app/artifacts/demand_features.pkl', 'wb') as f:
    pickle.dump(demand_features, f)
print(f"demand_features.pkl saved: {len(demand_features)} features")

with open('/app/artifacts/price_features.pkl', 'wb') as f:
    pickle.dump(price_features, f)
print(f"price_features.pkl saved: {len(price_features)} features")

print("Done. Both feature lists now match the trained models exactly.")
