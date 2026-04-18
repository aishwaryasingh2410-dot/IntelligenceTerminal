import os
import glob
import pandas as pd
import streamlit as st


# -----------------------------
# FIND PROJECT ROOT
# -----------------------------
CURRENT_FILE = os.path.abspath(__file__)

# backend/data_loader.py → go up one level → project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(CURRENT_FILE))

DATA_DIR = os.path.join(PROJECT_ROOT, "data")


# -----------------------------
# LOAD ALL CSV DATA
# -----------------------------
@st.cache_data
def load_all_data():

    files = glob.glob(os.path.join(DATA_DIR, "*.csv"))

    if not files:
        return pd.DataFrame()

    df = pd.concat(
        [pd.read_csv(f) for f in files],
        ignore_index=True
    )

    # clean columns
    df.columns = df.columns.str.strip().str.lower()

    # datetime parsing
    if "datetime" in df.columns:
        df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")

    return df


# -----------------------------
# EXPIRY LIST
# -----------------------------
def get_available_expiries():

    df = load_all_data()

    if df.empty or "expiry" not in df.columns:
        return []

    return sorted(df["expiry"].dropna().unique())


# -----------------------------
# LOAD EXPIRY DATA
# -----------------------------
def load_expiry_data(expiry):

    df = load_all_data()

    if df.empty:
        return df

    if "expiry" not in df.columns:
        return pd.DataFrame()

    return df[df["expiry"] == expiry]


# -----------------------------
# STRIKE FILTER
# -----------------------------
def filter_strike_range(df, strike_min, strike_max):

    if df.empty or "strike" not in df.columns:
        return df

    return df[
        (df["strike"] >= strike_min) &
        (df["strike"] <= strike_max)
    ]
