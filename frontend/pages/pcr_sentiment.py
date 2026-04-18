import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from backend.data_loader import load_expiry_data, filter_strike_range

st.title("📉 PCR Sentiment Dashboard")

expiry = st.session_state.get("expiry")
strike_range = st.session_state.get("strike_range")

if expiry is None:
    st.warning("Please select expiry from the main dashboard.")
    st.stop()

df = load_expiry_data(expiry)
if strike_range:
    df = filter_strike_range(df, strike_range[0], strike_range[1])
if df.empty:
    st.warning("No data available for selected filters.")
    st.stop()

temp = df.copy()
temp["pcr_volume"] = temp["volume_pe"] / (temp["volume_ce"] + 1)
temp["pcr_oi"] = temp["oi_pe"] / (temp["oi_ce"] + 1)
pcr = temp.groupby("datetime")[["pcr_volume", "pcr_oi"]].mean().reset_index()
latest_pcr = pcr["pcr_volume"].iloc[-1]

col1, col2 = st.columns(2)
col1.metric("📊 Latest PCR (Volume)", round(latest_pcr, 2))
col2.metric("Market Sentiment", "Bearish 🔴" if latest_pcr > 1 else "Bullish 🟢")

st.subheader("📊 PCR Trend")
fig = go.Figure()
fig.add_trace(go.Scatter(x=pcr["datetime"], y=pcr["pcr_volume"], name="Volume PCR"))
fig.add_trace(go.Scatter(x=pcr["datetime"], y=pcr["pcr_oi"], name="OI PCR"))
fig.add_hline(y=0.8, line_dash="dot", line_color="green")
fig.add_hline(y=1.0, line_dash="dash", line_color="yellow")
fig.add_hline(y=1.2, line_dash="dot", line_color="red")
fig.update_layout(template="plotly_dark", xaxis_title="Time", yaxis_title="PCR", hovermode="x unified")
st.plotly_chart(fig, use_container_width=True)

st.subheader("📊 PCR Distribution")
fig2 = px.histogram(pcr, x="pcr_volume", nbins=40, title="Distribution of Volume PCR", template="plotly_dark")
st.plotly_chart(fig2, use_container_width=True)

st.subheader("🧠 Market Insights")
if latest_pcr > 1.2:
    st.warning("High PCR → Strong Put Activity → Potential Bearish Sentiment")
elif latest_pcr < 0.8:
    st.success("Low PCR → Strong Call Activity → Potential Bullish Sentiment")
else:
    st.info("PCR indicates neutral sentiment")

st.subheader("📋 Data Preview")
st.dataframe(temp.head(50), use_container_width=True)
