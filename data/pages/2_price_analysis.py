import streamlit as st
import pandas as pd
import glob
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide")

# ----------------------------------------------------
# HEADER
# ----------------------------------------------------

st.title("📈 NIFTY Price Analysis")

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

    return df


df = load_data()

if df.empty:
    st.error("No data found in /data folder")
    st.stop()

# ----------------------------------------------------
# SIDEBAR FILTERS
# ----------------------------------------------------

st.sidebar.header("🔎 Filters")

expiry = st.sidebar.selectbox(
    "Select Expiry",
    sorted(df["expiry"].unique())
)

df = df[df["expiry"] == expiry]

# Strike filter
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
# SPOT PRICE TIMESERIES
# ----------------------------------------------------

st.subheader("📊 Spot Price Movement")

fig = px.line(
    df,
    x="datetime",
    y="spot_close",
    title="NIFTY Spot Price Over Time",
    markers=True
)

fig.update_layout(
    template="plotly_dark",
    hovermode="x unified"
)

st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------
# ATM STRIKE ANALYSIS
# ----------------------------------------------------

st.subheader("📍 ATM Option Price Movement")

# approximate ATM
df["distance_from_spot"] = abs(df["strike"] - df["spot_close"])

atm_df = df.loc[df.groupby("datetime")["distance_from_spot"].idxmin()]

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=atm_df["datetime"],
        y=atm_df["CE"],
        name="ATM Call Price",
        mode="lines"
    )
)

fig.add_trace(
    go.Scatter(
        x=atm_df["datetime"],
        y=atm_df["PE"],
        name="ATM Put Price",
        mode="lines"
    )
)

fig.update_layout(
    template="plotly_dark",
    title="ATM Option Prices Over Time"
)

st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------
# CE vs PE PRICE BY STRIKE
# ----------------------------------------------------

st.subheader("📊 Option Prices by Strike")

strike_df = df.groupby("strike")[["CE", "PE"]].mean().reset_index()

fig = px.line(
    strike_df,
    x="strike",
    y=["CE", "PE"],
    title="Average Option Prices by Strike"
)

fig.update_layout(template="plotly_dark")

st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------
# PRICE DISTRIBUTION
# ----------------------------------------------------

st.subheader("📊 Spot Price Distribution")

fig2 = px.histogram(
    df,
    x="spot_close",
    nbins=40,
    title="Spot Price Distribution"
)

fig2.update_layout(template="plotly_dark")

st.plotly_chart(fig2, use_container_width=True)

# ----------------------------------------------------
# VOLATILITY PROXY
# ----------------------------------------------------

st.subheader("📉 Price Volatility Proxy")

df["returns"] = df["spot_close"].pct_change()

volatility = df["returns"].rolling(20).std() * (252 ** 0.5)

fig3 = px.line(
    x=df["datetime"],
    y=volatility,
    labels={"x": "Datetime", "y": "Volatility"},
    title="Rolling Volatility (20 Period)"
)

fig3.update_layout(template="plotly_dark")

st.plotly_chart(fig3, use_container_width=True)

# ----------------------------------------------------
# DATA PREVIEW
# ----------------------------------------------------

st.subheader("📋 Data Preview")

st.dataframe(df.head(50), use_container_width=True)