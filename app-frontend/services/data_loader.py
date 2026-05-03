"""
Loads and engineers features from the raw energy CSV.
Used by Data Explorer and Forecasting pages to render historical charts
without calling the API for every point.
"""

import pandas as pd
import numpy as np
import streamlit as st
from utils.config import DATA_PATH


@st.cache_data(ttl=600)
def load_dataset() -> pd.DataFrame:
    """
    Load energy_dataset.csv and return a clean, feature-engineered DataFrame.
    Returns an empty DataFrame if the file is not found.
    """
    try:
        df = pd.read_csv(DATA_PATH)
        df['time'] = pd.to_datetime(df['time'], utc=True)
        df = df.sort_values('time').set_index('time')

        # Drop rows with null demand (36 nulls in dataset)
        df = df.dropna(subset=['total load actual'])

        # Derived features
        renewable_cols = [
            'generation solar', 'generation wind onshore',
            'generation hydro run-of-river and poundage',
            'generation hydro water reservoir', 'generation biomass'
        ]
        fossil_cols = ['generation fossil gas', 'generation fossil hard coal']

        df['renewable'] = df[renewable_cols].fillna(0).sum(axis=1)
        df['fossil']    = df[fossil_cols].fillna(0).sum(axis=1)
        df['nuclear']   = df['generation nuclear'].fillna(0)
        df['total_gen'] = df['renewable'] + df['fossil'] + df['nuclear']
        df['renewable_pct'] = (df['renewable'] / df['total_gen'].replace(0, np.nan) * 100).fillna(0)

        df['hour']       = df.index.hour
        df['day_of_week']= df.index.dayofweek
        df['month']      = df.index.month
        df['is_weekend'] = (df.index.dayofweek >= 5).astype(int)

        return df
    except FileNotFoundError:
        st.warning(f"Dataset not found at {DATA_PATH}. Historical charts will be unavailable.")
        return pd.DataFrame()


def get_feature_input_defaults(df: pd.DataFrame) -> dict:
    """Return median values for each feature — used to pre-fill input widgets."""
    if df.empty:
        return {}
    numeric = df.select_dtypes(include='number')
    return numeric.median().to_dict()
