import streamlit as st
import plotly.express as px
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from backend.data_loader import load_expiry_data, filter_strike_range

st.title("📊 Volatility Smile")

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

df.columns = df.columns.str.strip().str.lower()

if "ce" not in df.columns or "strike" not in df.columns:
    st.error("Missing required columns: strike, ce")
    st.stop()

iv = df.groupby("strike")["ce"].mean().reset_index()

st.subheader("📈 Volatility Smile Curve")
fig = px.line(iv, x="strike", y="ce", markers=True,
              title="Volatility Smile (Using CE Price Proxy)", template="plotly_dark")
st.plotly_chart(fig, use_container_width=True)

st.subheader("📋 Data Preview")
st.dataframe(df.head(50), use_container_width=True)