"""
Feature engineering service.
Computes exact feature vectors matching the trained model feature lists.
"""

# ─────────────────────────────────────────────────────────────────────────────
# Feature name lists matching the trained models in colab_modeltraining_v4.ipynb
# ─────────────────────────────────────────────────────────────────────────────

DEMAND_FEATURE_NAMES = [
    'day_of_week', 'month_sin', 'month_cos', 'is_weekend',
    'hour_sin', 'hour_cos',
    'demand_lag_1h', 'demand_lag_24h',
    'price_lag_1h',  'price_lag_24h',
    'renewable', 'fossil', 'nuclear',
    'renewable_pct',
    'demand_avg_24h', 'price_avg_24h',
    'forecast wind onshore day ahead',
    'forecast solar day ahead',
    'total load forecast',
]

PRICE_FEATURE_NAMES = [
    'day_of_week', 'month_sin', 'month_cos', 'is_weekend',
    'hour_sin', 'hour_cos',
    'price_lag_1h',  'price_lag_12h',
    'demand_lag_1h', 'demand_lag_12h',
    'forecast wind onshore day ahead',
    'forecast solar day ahead',
    'renewable', 'fossil', 'nuclear',
    'renewable_pct',
    'price_avg_24h', 'demand_avg_24h',
    'total load forecast',
]


def compute_generation_aggregates(raw: dict) -> dict:
    def get(key):
        val = raw.get(key, 0)
        return float(val) if val is not None else 0.0

    renewable = (
        get('generation solar') +
        get('generation wind onshore') +
        get('generation hydro run-of-river and poundage') +
        get('generation hydro water reservoir') +
        get('generation hydro pumped storage consumption') +
        get('generation biomass') +
        get('generation other renewable')
    )
    fossil = (
        get('generation fossil gas') +
        get('generation fossil hard coal') +
        get('generation fossil brown coal/lignite') +
        get('generation fossil oil')
    )
    nuclear   = get('generation nuclear')
    other     = get('generation other') + get('generation waste')
    total_gen = renewable + fossil + nuclear + other
    renewable_pct = (renewable / total_gen * 100.0) if total_gen > 0 else 0.0

    return {
        'renewable':     renewable,
        'fossil':        fossil,
        'nuclear':       nuclear,
        'other':         other,
        'total_gen':     total_gen,
        'renewable_pct': renewable_pct,
    }


def compute_time_features(time_str: str) -> dict:
    import math
    from datetime import datetime
    try:
        dt = datetime.fromisoformat(str(time_str))
    except Exception:
        dt = datetime.now()

    hour        = dt.hour
    day_of_week = dt.weekday()
    month       = dt.month
    is_weekend  = int(day_of_week >= 5)

    return {
        'hour':        hour,
        'day_of_week': day_of_week,
        'month':       month,
        'year':        dt.year,
        'is_weekend':  is_weekend,
        'hour_sin':    math.sin(2 * math.pi * hour        / 24),
        'hour_cos':    math.cos(2 * math.pi * hour        / 24),
        'month_sin':   math.sin(2 * math.pi * (month - 1) / 12),
        'month_cos':   math.cos(2 * math.pi * (month - 1) / 12),
        'dow_sin':     math.sin(2 * math.pi * day_of_week / 7),
        'dow_cos':     math.cos(2 * math.pi * day_of_week / 7),
    }


def build_demand_features(raw: dict) -> dict:
    gen  = compute_generation_aggregates(raw)
    time = compute_time_features(raw.get('time_str', ''))

    def get(key, default=0.0):
        val = raw.get(key, default)
        return float(val) if val is not None else float(default)

    return {
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
    }


def build_price_features(raw: dict) -> dict:
    gen  = compute_generation_aggregates(raw)
    time = compute_time_features(raw.get('time_str', ''))

    def get(key, default=0.0):
        val = raw.get(key, default)
        return float(val) if val is not None else float(default)

    return {
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
    }


def build_all_features(raw: dict) -> dict:
    gen  = compute_generation_aggregates(raw)
    return {
        'demand_features': build_demand_features(raw),
        'price_features':  build_price_features(raw),
        'generation_breakdown': {
            'Renewable':   gen['renewable'],
            'Fossil':      gen['fossil'],
            'Nuclear':     gen['nuclear'],
            'Other':       gen['other'],
            'Total':       gen['total_gen'],
            'Renewable %': round(gen['renewable_pct'], 1),
        },
        'time_info': compute_time_features(raw.get('time_str', '')),
    }
