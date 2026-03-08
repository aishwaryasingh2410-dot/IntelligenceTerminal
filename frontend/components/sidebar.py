import streamlit as st
from pathlib import Path

DATA_PATH = Path("data")

def dataset_selector():

    files = list(DATA_PATH.glob("*.csv"))
    expiries = [f.stem for f in files]

    selected = st.sidebar.selectbox(
        "Select Expiry Dataset",
        expiries
    )

    return selected