"""
Standardized raw feature input form.
All pages that need predictions import from here.
"""

import streamlit as st
from datetime import datetime


def render_raw_input_form(key_prefix: str = "") -> dict:
    """
    Renders all raw input widgets grouped by category.
    key_prefix: unique per page to avoid widget key conflicts.
    Returns dict of all raw values ready for feature engineering.
    """

    def k(name):
        return f"{key_prefix}{name}"

    # ── Timestamp ──────────────────────────────────────────────────────────
    st.markdown("##### Timestamp")
    col_d, col_t = st.columns(2)
    with col_d:
        date_val = st.date_input("Date", value=datetime(2018, 6, 15).date(), key=k("date"))
    with col_t:
        hour_val = st.selectbox("Hour (0–23)", list(range(24)),
                                 index=st.session_state.get("selected_hour", 14),
                                 key=k("hour"))
    time_str = f"{date_val} {hour_val:02d}:00:00"

    st.divider()

    # ── Renewable generation ───────────────────────────────────────────────
    st.markdown("##### Renewable Generation (MW)")
    r1, r2, r3 = st.columns(3)
    with r1:
        gen_solar    = st.number_input("Solar",              0.0, 12000.0, 4500.0, 50.0, key=k("solar"))
        gen_biomass  = st.number_input("Biomass",            0.0,  5000.0,  500.0, 50.0, key=k("biomass"))
    with r2:
        gen_wind     = st.number_input("Wind onshore",       0.0, 20000.0, 8000.0, 50.0, key=k("wind"))
        gen_other_r  = st.number_input("Other renewable",    0.0,  3000.0,  300.0, 50.0, key=k("other_r"))
    with r3:
        gen_hydro_r  = st.number_input("Hydro run-of-river", 0.0,  8000.0, 1500.0, 50.0, key=k("hydro_r"))
        gen_hydro_w  = st.number_input("Hydro reservoir",    0.0, 10000.0, 2000.0, 50.0, key=k("hydro_w"))
        gen_hydro_p  = st.number_input("Hydro pumped stor.", 0.0,  5000.0,  500.0, 50.0, key=k("hydro_p"))

    st.divider()

    # ── Fossil generation ──────────────────────────────────────────────────
    st.markdown("##### Fossil Generation (MW)")
    f1, f2 = st.columns(2)
    with f1:
        gen_gas      = st.number_input("Fossil gas",         0.0, 15000.0, 4000.0, 50.0, key=k("gas"))
        gen_coal     = st.number_input("Fossil hard coal",   0.0, 12000.0, 1500.0, 50.0, key=k("coal"))
    with f2:
        gen_lignite  = st.number_input("Brown coal/lignite", 0.0,  5000.0,  200.0, 50.0, key=k("lignite"))
        gen_oil      = st.number_input("Fossil oil",         0.0,  3000.0,  100.0, 50.0, key=k("oil"))

    st.divider()

    # ── Other generation ───────────────────────────────────────────────────
    st.markdown("##### Other Generation (MW)")
    o1, o2 = st.columns(2)
    with o1:
        gen_nuclear  = st.number_input("Nuclear",  0.0, 10000.0, 7000.0, 50.0, key=k("nuclear"))
        gen_other    = st.number_input("Other",    0.0,  3000.0,  400.0, 50.0, key=k("other"))
    with o2:
        gen_waste    = st.number_input("Waste",    0.0,  2000.0,  250.0, 50.0, key=k("waste"))

    st.divider()

    # ── Forecasts ──────────────────────────────────────────────────────────
    st.markdown("##### Day-Ahead Forecasts (MW)")
    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        fc_solar     = st.number_input("Forecast solar",     0.0, 12000.0, 4200.0, 50.0, key=k("fc_solar"))
    with fc2:
        fc_wind      = st.number_input("Forecast wind",      0.0, 20000.0, 7800.0, 50.0, key=k("fc_wind"))
    with fc3:
        fc_load      = st.number_input("Total load forecast",0.0, 50000.0,28000.0,100.0, key=k("fc_load"))

    st.divider()

    # ── Lag features ───────────────────────────────────────────────────────
    st.markdown("##### Lag Features")
    if True:
        l1, l2, l3 = st.columns(3)
        with l1:
            lag_d_1h   = st.number_input("Demand lag 1h",  0.0, 50000.0, 28000.0, 100.0, key=k("lag_d_1h"))
            lag_p_1h   = st.number_input("Price lag 1h",   0.0,   250.0,    58.0,   0.5, key=k("lag_p_1h"))
        with l2:
            lag_d_12h  = st.number_input("Demand lag 12h", 0.0, 50000.0, 27200.0, 100.0, key=k("lag_d_12h"))
            lag_p_12h  = st.number_input("Price lag 12h",  0.0,   250.0,    57.0,   0.5, key=k("lag_p_12h"))
        with l3:
            lag_d_24h  = st.number_input("Demand lag 24h", 0.0, 50000.0, 27500.0, 100.0, key=k("lag_d_24h"))
            lag_p_24h  = st.number_input("Price lag 24h",  0.0,   250.0,    57.5,   0.5, key=k("lag_p_24h"))

    st.markdown("##### Rolling Average Features")
    if True:
        ra1, ra2 = st.columns(2)
        with ra1:
            d_avg_24h  = st.number_input("Demand avg 24h (MW)", 0.0, 50000.0, 27800.0, 100.0, key=k("d_avg"))
        with ra2:
            p_avg_24h  = st.number_input("Price avg 24h (EUR)", 0.0,   250.0,    58.0,   0.5, key=k("p_avg"))

    # ── Return raw dict ────────────────────────────────────────────────────
    return {
        "time_str":                                    time_str,
        "generation solar":                            gen_solar,
        "generation wind onshore":                     gen_wind,
        "generation hydro run-of-river and poundage":  gen_hydro_r,
        "generation hydro water reservoir":            gen_hydro_w,
        "generation hydro pumped storage consumption": gen_hydro_p,
        "generation biomass":                          gen_biomass,
        "generation other renewable":                  gen_other_r,
        "generation fossil gas":                       gen_gas,
        "generation fossil hard coal":                 gen_coal,
        "generation fossil brown coal/lignite":        gen_lignite,
        "generation fossil oil":                       gen_oil,
        "generation nuclear":                          gen_nuclear,
        "generation other":                            gen_other,
        "generation waste":                            gen_waste,
        "forecast wind onshore day ahead":             fc_wind,
        "forecast solar day ahead":                    fc_solar,
        "total load forecast":                         fc_load,
        "demand_lag_1h":                               lag_d_1h,
        "demand_lag_12h":                              lag_d_12h,
        "demand_lag_24h":                              lag_d_24h,
        "price_lag_1h":                                lag_p_1h,
        "price_lag_12h":                               lag_p_12h,
        "price_lag_24h":                               lag_p_24h,
        "demand_avg_24h":                              d_avg_24h,
        "price_avg_24h":                               p_avg_24h,
    }
