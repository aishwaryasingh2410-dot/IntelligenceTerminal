import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.ensemble import IsolationForest

from backend.data_loader import load_all_data

st.title("🤖 AI Unusual Options Activity Detector")

# ---------------------------------------------------
# DATA LOADING
# ---------------------------------------------------

df = load_all_data()

if df.empty:
    st.warning("⚠ No CSV files found in data folder")
    st.stop()

# normalize column names
df.columns = df.columns.str.strip().str.lower()

# ---------------------------------------------------
# FEATURE ENGINEERING
# ---------------------------------------------------

required_cols = ["volume_ce","volume_pe","oi_ce","oi_pe","strike","datetime"]

missing = [c for c in required_cols if c not in df.columns]

if missing:
    st.error(f"Missing required columns: {missing}")
    st.stop()

df["total_volume"] = df["volume_ce"] + df["volume_pe"]
df["total_oi"] = df["oi_ce"] + df["oi_pe"]

# ---------------------------------------------------
# SIDEBAR MODEL SETTINGS
# ---------------------------------------------------

st.sidebar.header("⚙ AI Model Settings")

contamination = st.sidebar.slider(
    "Anomaly Sensitivity",
    0.01,
    0.10,
    0.02,
    help="Higher value = detect more anomalies"
)

# ---------------------------------------------------
# MODEL TRAINING
# ---------------------------------------------------

features = df[["total_volume", "total_oi"]].fillna(0)

model = IsolationForest(
    contamination=contamination,
    random_state=42
)

df["anomaly"] = model.fit_predict(features)

df["anomaly_label"] = df["anomaly"].map({
    1: "Normal",
    -1: "Anomaly"
})

# ---------------------------------------------------
# SUMMARY METRICS
# ---------------------------------------------------

total_rows = len(df)
total_anomalies = (df["anomaly"] == -1).sum()

col1, col2 = st.columns(2)

col1.metric("Total Data Points", total_rows)
col2.metric("⚠ Detected Anomalies", total_anomalies)

# ---------------------------------------------------
# MARKET INSIGHT
# ---------------------------------------------------

st.subheader("📊 Market Insight")

if total_anomalies > 20:
    st.error("🚨 Significant unusual options activity detected")

elif total_anomalies > 5:
    st.warning("⚠ Moderate unusual activity detected")

elif total_anomalies > 0:
    st.info("Some unusual trades detected")

else:
    st.success("No abnormal activity detected")

# ---------------------------------------------------
# VISUALIZATION
# ---------------------------------------------------

st.subheader("📈 AI Detected Options Activity")

fig = px.scatter(
    df,
    x="strike",
    y="total_volume",
    size="total_oi",
    color="anomaly_label",
    title="AI Detected Unusual Options Activity",
    hover_data=["datetime","total_volume","total_oi"]
)

st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------
# ANOMALY TABLE
# ---------------------------------------------------

st.subheader("🚨 Unusual Activity Detected")

anomalies = df[df["anomaly"] == -1][
    ["datetime","strike","total_volume","total_oi"]
]

if anomalies.empty:
    st.success("No anomalies detected in dataset")
else:
    st.dataframe(anomalies, use_container_width=True)
