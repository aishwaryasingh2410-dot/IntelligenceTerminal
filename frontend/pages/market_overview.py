import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from backend.data_loader import load_expiry_data, filter_strike_range

st.title("📊 Market Overview")

expiry = st.session_state.get("expiry")
strike_range = st.session_state.get("strike_range")

if expiry is None:
    st.warning("Please select expiry from main dashboard.")
    st.stop()

df = load_expiry_data(expiry)
if strike_range:
    df = filter_strike_range(df, strike_range[0], strike_range[1])
if df.empty:
    st.warning("No data available for selected filters.")
    st.stop()

spot = round(df["spot_close"].iloc[-1], 2)
total_volume = int(df["volume_ce"].sum() + df["volume_pe"].sum())
total_oi = int(df["oi_ce"].sum() + df["oi_pe"].sum())
avg_pcr = round(df["volume_pe"].sum() / (df["volume_ce"].sum() + 1), 2)

col1, col2, col3, col4 = st.columns(4)
col1.metric("NIFTY Spot", spot)
col2.metric("Total Volume", f"{total_volume:,}")
col3.metric("Total Open Interest", f"{total_oi:,}")
col4.metric("PCR", avg_pcr)
st.divider()

st.subheader("📊 PCR Sentiment Indicator")
fig = go.Figure(go.Indicator(
    mode="gauge+number", value=avg_pcr,
    title={"text": "Put Call Ratio"},
    gauge={"axis": {"range": [0, 2]}, "steps": [
        {"range": [0, 0.8], "color": "#ff4b4b"},
        {"range": [0.8, 1.2], "color": "#888"},
        {"range": [1.2, 2], "color": "#2ecc71"}
    ]}
))
st.plotly_chart(fig, use_container_width=True)

st.subheader("📌 Open Interest Distribution")
oi_df = df.groupby("strike")[["oi_ce", "oi_pe"]].sum().reset_index()
fig = px.bar(oi_df, x="strike", y=["oi_ce", "oi_pe"], barmode="group", template="plotly_dark")
fig.add_vline(x=spot, line_dash="dash", line_color="yellow")
st.plotly_chart(fig, use_container_width=True)

st.subheader("📊 Volume Distribution")
vol_df = df.groupby("strike")[["volume_ce", "volume_pe"]].sum().reset_index()
fig = px.bar(vol_df, x="strike", y=["volume_ce", "volume_pe"], barmode="group", template="plotly_dark")
fig.add_vline(x=spot, line_dash="dash", line_color="yellow")
st.plotly_chart(fig, use_container_width=True)

st.subheader("📍 Key Market Levels")
max_call = oi_df.loc[oi_df["oi_ce"].idxmax(), "strike"]
max_put = oi_df.loc[oi_df["oi_pe"].idxmax(), "strike"]
c1, c2 = st.columns(2)
c1.success(f"📉 Resistance Level: {max_call}")
c2.success(f"📈 Support Level: {max_put}")

st.subheader("🧠 Market Signal")
signal = "Neutral"
if avg_pcr > 1.2 and max_put > max_call:
    signal = "Bullish"
elif avg_pcr < 0.8 and max_call > max_put:
    signal = "Bearish"
st.info(f"📡 Market Signal: {signal}")