import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from backend.data_loader import load_expiry_data, filter_strike_range

st.title("📈 NIFTY Price Analysis")

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

# normalize columns
df.columns = df.columns.str.strip().str.lower()

required_cols = ["datetime", "spot_close", "strike", "ce", "pe"]
for col in required_cols:
    if col not in df.columns:
        st.error(f"Missing required column: {col}")
        st.stop()

st.subheader("📊 Spot Price Movement")
fig = px.line(df, x="datetime", y="spot_close", title="NIFTY Spot Price Over Time",
              markers=True, template="plotly_dark")
st.plotly_chart(fig, use_container_width=True)

st.subheader("📍 ATM Option Price Movement")
temp = df.copy()
temp["distance_from_spot"] = abs(temp["strike"] - temp["spot_close"])
try:
    atm_df = temp.loc[temp.groupby("datetime")["distance_from_spot"].idxmin()]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=atm_df["datetime"], y=atm_df["ce"], name="ATM Call Price", mode="lines"))
    fig.add_trace(go.Scatter(x=atm_df["datetime"], y=atm_df["pe"], name="ATM Put Price", mode="lines"))
    fig.update_layout(template="plotly_dark", title="ATM Option Prices Over Time")
    st.plotly_chart(fig, use_container_width=True)
except Exception:
    st.warning("Could not compute ATM strike.")

st.subheader("📊 Option Prices by Strike")
strike_df = df.groupby("strike")[["ce", "pe"]].mean().reset_index()
fig = px.line(strike_df, x="strike", y=["ce", "pe"], title="Average Option Prices by Strike", template="plotly_dark")
st.plotly_chart(fig, use_container_width=True)

st.subheader("📊 Spot Price Distribution")
fig2 = px.histogram(df, x="spot_close", nbins=40, title="Spot Price Distribution", template="plotly_dark")
st.plotly_chart(fig2, use_container_width=True)

st.subheader("📉 Price Volatility Proxy")
temp["returns"] = temp["spot_close"].pct_change()
temp["volatility"] = temp["returns"].rolling(20).std() * (252 ** 0.5)
fig3 = px.line(temp, x="datetime", y="volatility", title="Rolling Volatility (20 Period)", template="plotly_dark")
st.plotly_chart(fig3, use_container_width=True)

st.subheader("📋 Data Preview")
st.dataframe(df.head(50), use_container_width=True)
