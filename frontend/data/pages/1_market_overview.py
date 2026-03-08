import streamlit as st
import pandas as pd
import glob
import plotly.express as px
import plotly.graph_objects as go
from sklearn.ensemble import IsolationForest

st.set_page_config(layout="wide")

# ----------------------------------------------------
# HEADER
# ----------------------------------------------------

st.title("📊 NIFTY Options Market Dashboard")

# ----------------------------------------------------
# DATA LOADING
# ----------------------------------------------------

@st.cache_data
def load_data():
    files = glob.glob("data/*.csv")

    if len(files) == 0:
        return pd.DataFrame()

    df = pd.concat([pd.read_csv(file) for file in files])

    df["datetime"] = pd.to_datetime(df["datetime"])

    df["total_volume"] = df["volume_CE"] + df["volume_PE"]
    df["total_oi"] = df["oi_CE"] + df["oi_PE"]
    df["PCR"] = df["volume_PE"] / (df["volume_CE"] + 1)

    return df


df = load_data()

if df.empty:
    st.error("No data found in /data folder")
    st.stop()

# ----------------------------------------------------
# SIDEBAR FILTERS
# ----------------------------------------------------

st.sidebar.header("🔎 Market Filters")

expiry = st.sidebar.selectbox(
    "Select Expiry",
    sorted(df["expiry"].unique())
)

df = df[df["expiry"] == expiry]

strike_min = int(df["strike"].min())
strike_max = int(df["strike"].max())

strike_range = st.sidebar.slider(
    "Strike Range",
    strike_min,
    strike_max,
    (strike_min, strike_max)
)

df = df[(df["strike"] >= strike_range[0]) & (df["strike"] <= strike_range[1])]

# ----------------------------------------------------
# MARKET METRICS
# ----------------------------------------------------

st.subheader("📈 Market Overview")

spot = round(df["spot_close"].iloc[-1], 2)
total_volume = int(df["total_volume"].sum())
total_oi = int(df["total_oi"].sum())
avg_pcr = round(df["PCR"].mean(), 2)

col1, col2, col3, col4 = st.columns(4)

col1.metric("NIFTY Spot", spot)
col2.metric("Total Volume", f"{total_volume:,}")
col3.metric("Total Open Interest", f"{total_oi:,}")
col4.metric("Average PCR", avg_pcr)

st.divider()

# ----------------------------------------------------
# PCR GAUGE
# ----------------------------------------------------

st.subheader("📊 PCR Sentiment Indicator")

fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=avg_pcr,
    title={'text': "Put Call Ratio"},
    gauge={
        'axis': {'range': [0, 2]},
        'steps': [
            {'range': [0, 0.8], 'color': "#ff4b4b"},
            {'range': [0.8, 1.2], 'color': "#888"},
            {'range': [1.2, 2], 'color': "#2ecc71"}
        ]
    }
))

st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------
# OI DISTRIBUTION
# ----------------------------------------------------

st.subheader("📌 Open Interest Distribution")

oi_df = df.groupby("strike")[["oi_CE", "oi_PE"]].sum().reset_index()

fig = px.bar(
    oi_df,
    x="strike",
    y=["oi_CE", "oi_PE"],
    barmode="group",
    title="Open Interest by Strike"
)

fig.add_vline(x=spot, line_dash="dash", line_color="yellow")

st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------
# VOLUME DISTRIBUTION
# ----------------------------------------------------

st.subheader("📊 Volume Distribution")

vol_df = df.groupby("strike")[["volume_CE", "volume_PE"]].sum().reset_index()

fig = px.bar(
    vol_df,
    x="strike",
    y=["volume_CE", "volume_PE"],
    barmode="group",
    title="Volume by Strike"
)

fig.add_vline(x=spot, line_dash="dash", line_color="yellow")

st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------
# SUPPORT / RESISTANCE LEVELS
# ----------------------------------------------------

st.subheader("📍 Key Market Levels")

max_call = oi_df.loc[oi_df["oi_CE"].idxmax(), "strike"]
max_put = oi_df.loc[oi_df["oi_PE"].idxmax(), "strike"]

col1, col2 = st.columns(2)

col1.success(f"📉 Resistance Level (Max Call OI): {max_call}")
col2.success(f"📈 Support Level (Max Put OI): {max_put}")

# ----------------------------------------------------
# MARKET SIGNAL
# ----------------------------------------------------

st.subheader("🧠 AI Market Signal")

signal = "Neutral"

if avg_pcr > 1.2 and max_put > max_call:
    signal = "Bullish"

elif avg_pcr < 0.8 and max_call > max_put:
    signal = "Bearish"

st.info(f"📡 Market Signal: {signal}")

# ----------------------------------------------------
# ANOMALY DETECTION
# ----------------------------------------------------

@st.cache_resource
def train_anomaly_model(data):
    model = IsolationForest(contamination=0.02)
    model.fit(data)
    return model


features = df[["oi_CE", "oi_PE", "volume_CE", "volume_PE"]]

model = train_anomaly_model(features)

df["anomaly"] = model.predict(features)

anomalies = df[df["anomaly"] == -1]

st.subheader("🚨 Unusual Market Activity")

if len(anomalies) > 0:
    st.dataframe(anomalies.head(10), use_container_width=True)
else:
    st.success("No unusual market activity detected")

# ----------------------------------------------------
# DATA PREVIEW
# ----------------------------------------------------

st.subheader("📋 Dataset Preview")

st.dataframe(df.head(50), use_container_width=True)