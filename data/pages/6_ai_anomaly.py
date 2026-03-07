import streamlit as st
import pandas as pd
import glob
import plotly.express as px
from sklearn.ensemble import IsolationForest

st.set_page_config(
    page_title="Options Intelligence Terminal",
    layout="wide",
    page_icon="📊"
)

st.markdown("""
<style>
.stApp {
    background-color: #0E1117;
}

[data-testid="stSidebar"] {
    background-color: #161B22;
}

h1,h2,h3,h4 {
    color: white;
}

.block-container {
    padding-top: 2rem;
}

.metric-container {
    background-color: #161B22;
    border-radius: 10px;
    padding: 15px;
}
</style>
""", unsafe_allow_html=True)

st.set_page_config(layout="wide")

st.title("🤖 AI Unusual Options Activity Detector")

# Load data
files = glob.glob("data/*.csv")

if not files:
    st.warning("No CSV files found in data folder")
    st.stop()

df = pd.concat([pd.read_csv(file) for file in files])

# Feature engineering
df["total_volume"] = df["volume_CE"] + df["volume_PE"]
df["total_oi"] = df["oi_CE"] + df["oi_PE"]

# Sidebar
st.sidebar.header("Model Settings")

contamination = st.sidebar.slider(
    "Anomaly Sensitivity",
    0.01,
    0.10,
    0.02
)

# Isolation Forest Model
features = df[["total_volume","total_oi"]]

model = IsolationForest(
    contamination=contamination,
    random_state=42
)

df["anomaly"] = model.fit_predict(features)

# Summary
total_anomalies = len(df[df["anomaly"]==-1])

st.metric("⚠ Detected Anomalies", total_anomalies)

total_anomalies = len(df[df["anomaly"] == -1])

st.metric("⚠ Detected Anomalies", total_anomalies)

# Insights section
st.subheader("📊 Market Insights")

if total_anomalies > 5:
    st.error("Unusual trading activity detected")

elif total_anomalies > 0:
    st.warning("Some unusual activity detected")

else:
    st.success("No abnormal activity detected")

# Scatter Plot
fig = px.scatter(
    df,
    x="strike",
    y="total_volume",
    size="total_oi",
    color="anomaly",
    title="AI Detected Unusual Options Activity",
    color_discrete_map={
        1:"#22c55e",
        -1:"#ef4444"
    },
    hover_data=["datetime","total_volume","total_oi"]
)

fig.update_layout(
    template="plotly_dark",
    plot_bgcolor="#0E1117",
    paper_bgcolor="#0E1117",
    font=dict(color="white"),
    xaxis_title="Strike Price",
    yaxis_title="Total Volume"
)

st.plotly_chart(fig, use_container_width=True)

# Anomaly Table
st.subheader("🚨 Unusual Activity Detected")

anomalies = df[df["anomaly"]==-1][
    ["datetime","strike","total_volume","total_oi"]
]

st.dataframe(anomalies, use_container_width=True)