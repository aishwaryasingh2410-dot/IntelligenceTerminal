import streamlit as st
import plotly.express as px
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from backend.data_loader import load_expiry_data, filter_strike_range

st.title("📊 Open Interest Analysis")

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

oi_group = df.groupby("strike")[["oi_ce", "oi_pe"]].sum().reset_index()

st.subheader("📊 Call vs Put Open Interest")
fig = px.bar(oi_group, x="strike", y=["oi_ce", "oi_pe"], barmode="group",
             title="Call vs Put Open Interest by Strike", template="plotly_dark")
st.plotly_chart(fig, use_container_width=True)

st.subheader("📈 Market Bias (Put - Call OI)")
oi_group["oi_diff"] = oi_group["oi_pe"] - oi_group["oi_ce"]
fig2 = px.bar(oi_group, x="strike", y="oi_diff",
              title="Put - Call Open Interest", template="plotly_dark")
st.plotly_chart(fig2, use_container_width=True)

st.subheader("📍 Key OI Levels")
max_call = oi_group.loc[oi_group["oi_ce"].idxmax(), "strike"]
max_put = oi_group.loc[oi_group["oi_pe"].idxmax(), "strike"]
col1, col2 = st.columns(2)
col1.metric("Resistance (Max Call OI)", max_call)
col2.metric("Support (Max Put OI)", max_put)

st.subheader("🔥 Open Interest Heatmap")
if "datetime" in df.columns:
    heatmap_df = df.pivot_table(values="oi_ce", index="strike", columns="datetime", aggfunc="sum")
    fig3 = px.imshow(heatmap_df, aspect="auto", title="Call Open Interest Heatmap", template="plotly_dark")
    st.plotly_chart(fig3, use_container_width=True)

st.subheader("📋 Data Preview")
st.dataframe(df.head(50), use_container_width=True)