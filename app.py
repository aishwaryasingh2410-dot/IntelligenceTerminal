import streamlit as st
import pandas as pd
import glob
from pathlib import Path

st.set_page_config(
    page_title="NIFTY Options Intelligence",
    page_icon="📊",
    layout="wide"
)

st.title("📊 NIFTY Options Market Intelligence Dashboard")

DATA_FOLDER = "data"


# --------------------------------------------------
# LOAD DATASETS
# --------------------------------------------------

@st.cache_data
def get_datasets():

    files = glob.glob(f"{DATA_FOLDER}/*.csv")

    return files


datasets = get_datasets()

st.sidebar.header("⚙ Dashboard Controls")

if len(datasets) == 0:

    st.sidebar.warning("No datasets found in data folder")

    st.metric("📂 Datasets Loaded", 0)
    st.metric("🗂 Selected Dataset", "None")

    st.stop()

# --------------------------------------------------
# DATASET SELECTOR
# --------------------------------------------------

dataset_names = [Path(f).stem for f in datasets]

selected_dataset = st.sidebar.selectbox(
    "Select Dataset",
    dataset_names
)

file_path = f"{DATA_FOLDER}/{selected_dataset}.csv"

df = pd.read_csv(file_path)

# --------------------------------------------------
# DATA PREPROCESSING
# --------------------------------------------------

df["datetime"] = pd.to_datetime(df["datetime"])

df["total_volume"] = df["volume_CE"] + df["volume_PE"]
df["total_oi"] = df["oi_CE"] + df["oi_PE"]

df["PCR"] = df["volume_PE"] / (df["volume_CE"] + 1)

# --------------------------------------------------
# DASHBOARD STATUS
# --------------------------------------------------

col1, col2, col3 = st.columns(3)

col1.metric("📂 Datasets Loaded", len(datasets))
col2.metric("🗂 Selected Dataset", selected_dataset)
col3.metric("🟢 Dashboard Status", "Online")

st.divider()

# --------------------------------------------------
# DATA PREVIEW
# --------------------------------------------------

st.subheader("📋 Dataset Preview")

st.dataframe(df.head(50), use_container_width=True)