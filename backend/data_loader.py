from pathlib import Path
import streamlit as st
import pandas as pd

DATA_PATH = Path("backend/data")


@st.cache_data
def get_available_expiries():

    if not DATA_PATH.exists():
        return []

    files = list(DATA_PATH.glob("*.csv"))
    expiries = [f.stem for f in files]
    expiries.sort()

    return expiries


@st.cache_data
def load_expiry_data(expiry):

    file_path = DATA_PATH / f"{expiry}.csv"

    if not file_path.exists():
        return pd.DataFrame()

    df = pd.read_csv(file_path)

    df.columns = df.columns.str.strip().str.lower()

    if "datetime" in df.columns:
        df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")

    return df