with open('/app/services/feature_engineering.py', 'r') as f:
    content = f.read()

# Fix build_demand_features — add timestamp as first key
old = """    return {
        'day_of_week':                     time['day_of_week'],
        'month_sin':                       time['month_sin'],
        'month_cos':                       time['month_cos'],
        'is_weekend':                      time['is_weekend'],
        'hour_sin':                        time['hour_sin'],
        'hour_cos':                        time['hour_cos'],
        'demand_lag_1h':                   get('demand_lag_1h',   28000.0),
        'demand_lag_24h':                  get('demand_lag_24h',  27500.0),
        'price_lag_1h':                    get('price_lag_1h',    58.0),
        'price_lag_24h':                   get('price_lag_24h',   57.5),
        'renewable':                       gen['renewable'],
        'fossil':                          gen['fossil'],
        'nuclear':                         gen['nuclear'],
        'renewable_pct':                   gen['renewable_pct'],
        'demand_avg_24h':                  get('demand_avg_24h',  27800.0),
        'price_avg_24h':                   get('price_avg_24h',   58.0),
        'forecast wind onshore day ahead': get('forecast wind onshore day ahead', 7800.0),
        'forecast solar day ahead':        get('forecast solar day ahead',        4200.0),
        'total load forecast':             get('total load forecast',             28000.0),
    }"""

new = """    return {
        'timestamp':                       raw.get('time_str', '2018-01-01 00:00:00'),
        'day_of_week':                     time['day_of_week'],
        'month_sin':                       time['month_sin'],
        'month_cos':                       time['month_cos'],
        'is_weekend':                      time['is_weekend'],
        'hour_sin':                        time['hour_sin'],
        'hour_cos':                        time['hour_cos'],
        'demand_lag_1h':                   get('demand_lag_1h',   28000.0),
        'demand_lag_24h':                  get('demand_lag_24h',  27500.0),
        'price_lag_1h':                    get('price_lag_1h',    58.0),
        'price_lag_24h':                   get('price_lag_24h',   57.5),
        'renewable':                       gen['renewable'],
        'fossil':                          gen['fossil'],
        'nuclear':                         gen['nuclear'],
        'renewable_pct':                   gen['renewable_pct'],
        'demand_avg_24h':                  get('demand_avg_24h',  27800.0),
        'price_avg_24h':                   get('price_avg_24h',   58.0),
        'forecast wind onshore day ahead': get('forecast wind onshore day ahead', 7800.0),
        'forecast solar day ahead':        get('forecast solar day ahead',        4200.0),
        'total load forecast':             get('total load forecast',             28000.0),
    }"""

if old in content:
    content = content.replace(old, new)
    print("Fix 1 applied: timestamp added to build_demand_features")
else:
    print("Fix 1 ERROR: pattern not found")

# Fix build_price_features — add timestamp as first key
old2 = """    return {
        'day_of_week':                     time['day_of_week'],
        'month_sin':                       time['month_sin'],
        'month_cos':                       time['month_cos'],
        'is_weekend':                      time['is_weekend'],
        'hour_sin':                        time['hour_sin'],
        'hour_cos':                        time['hour_cos'],
        'price_lag_1h':                    get('price_lag_1h',    58.0),
        'price_lag_12h':                   get('price_lag_12h',   57.0),
        'demand_lag_1h':                   get('demand_lag_1h',   28000.0),
        'demand_lag_12h':                  get('demand_lag_12h',  27200.0),
        'forecast wind onshore day ahead': get('forecast wind onshore day ahead', 7800.0),
        'forecast solar day ahead':        get('forecast solar day ahead',        4200.0),
        'renewable':                       gen['renewable'],
        'fossil':                          gen['fossil'],
        'nuclear':                         gen['nuclear'],
        'renewable_pct':                   gen['renewable_pct'],
        'price_avg_24h':                   get('price_avg_24h',   58.0),
        'demand_avg_24h':                  get('demand_avg_24h',  27800.0),
        'total load forecast':             get('total load forecast', 28000.0),
    }"""

new2 = """    return {
        'timestamp':                       raw.get('time_str', '2018-01-01 00:00:00'),
        'day_of_week':                     time['day_of_week'],
        'month_sin':                       time['month_sin'],
        'month_cos':                       time['month_cos'],
        'is_weekend':                      time['is_weekend'],
        'hour_sin':                        time['hour_sin'],
        'hour_cos':                        time['hour_cos'],
        'price_lag_1h':                    get('price_lag_1h',    58.0),
        'price_lag_12h':                   get('price_lag_12h',   57.0),
        'demand_lag_1h':                   get('demand_lag_1h',   28000.0),
        'demand_lag_12h':                  get('demand_lag_12h',  27200.0),
        'forecast wind onshore day ahead': get('forecast wind onshore day ahead', 7800.0),
        'forecast solar day ahead':        get('forecast solar day ahead',        4200.0),
        'renewable':                       gen['renewable'],
        'fossil':                          gen['fossil'],
        'nuclear':                         gen['nuclear'],
        'renewable_pct':                   gen['renewable_pct'],
        'price_avg_24h':                   get('price_avg_24h',   58.0),
        'demand_avg_24h':                  get('demand_avg_24h',  27800.0),
        'total load forecast':             get('total load forecast', 28000.0),
    }"""

if old2 in content:
    content = content.replace(old2, new2)
    print("Fix 2 applied: timestamp added to build_price_features")
else:
    print("Fix 2 ERROR: pattern not found")

with open('/app/services/feature_engineering.py', 'w') as f:
    f.write(content)

print("Done.")
